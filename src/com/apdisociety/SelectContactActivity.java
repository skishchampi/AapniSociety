package com.apdisociety;

import java.util.LinkedList;
import java.util.List;

import android.app.Activity;
import android.content.Context;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.provider.BaseColumns;
import android.provider.ContactsContract.CommonDataKinds.Email;
import android.provider.ContactsContract.CommonDataKinds.Phone;
import android.provider.ContactsContract.CommonDataKinds.Photo;
import android.provider.ContactsContract.Contacts;
import android.provider.ContactsContract.Data;
import android.provider.ContactsContract.RawContacts;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ListView;
import android.widget.RatingBar;
import android.widget.RatingBar.OnRatingBarChangeListener;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

public class SelectContactActivity extends Activity {
	
	public static String cnum;
	public static String value;
	public String cname;
	public String ctype;
	private final List<SpinnerEntry> spinnerContent = new LinkedList<SpinnerEntry>();
	private Spinner contactSpinner;
	public Spinner typeSpinner;
	private ListView contactListView;
	private final ContactsSpinnerAdapater adapter = new ContactsSpinnerAdapater(
			spinnerContent, this);
	private RatingBar ratingBar;
	RestService r;

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		
		
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.activity_select_contact);
		
		contactSpinner = (Spinner) findViewById(R.id.contactsSpinner);
		// typeSpinner = (Spinner)findViewById(R.id.spinner1);
		// contactListView = (ListView)findViewById(R.id.contactsListView);

		contactSpinner.setOnItemSelectedListener(new OnItemSelectedListener() {

			@Override
			public void onItemSelected(AdapterView<?> parent, View view,
					int position, long id) {
				updateList(position);
			}

			@Override
			public void onNothingSelected(AdapterView<?> parent) {
				updateList(contactSpinner.getSelectedItemPosition());
			}

			private void updateList(int position) {

				if (position < adapter.getCount() && position >= 0) {

					SpinnerEntry currentEntry = adapter.getItem(position);
					cname = adapter.getItem(position).getContactName();
					// contactListView.setAdapter(null);
					final List<ListViewEntry> content = new LinkedList<ListViewEntry>();
					queryAllPhoneNumbersForContact(currentEntry.getContactId(),
							content);
					queryAllEmailAddressesForContact(
							currentEntry.getContactId(), content);
					// contactListView.setAdapter(new
					// ContactListViewAdapter(content,SelectContactActivity.this));
				}
			}

		});

		/*
		 * typeSpinner.setOnItemSelectedListener(new OnItemSelectedListener() {
		 * 
		 * public void onItemSelected(AdapterView<?> parent, View view, int
		 * position, long id) { //updateList(position); ctype =
		 * String.valueOf(typeSpinner.getSelectedItem()); }
		 * 
		 * public void onNothingSelected(AdapterView<?> parent) {
		 * //updateList(contactSpinner.getSelectedItemPosition()); }
		 * 
		 * /*private void updateList(int position) {
		 * 
		 * if(position < adapter.getCount() && position >= 0) {
		 * 
		 * SpinnerEntry currentEntry = adapter.getItem(position); //
		 * contactListView.setAdapter(null); final List<ListViewEntry> content =
		 * new LinkedList<ListViewEntry>();
		 * queryAllPhoneNumbersForContact(currentEntry.getContactId(), content);
		 * queryAllEmailAddressesForContact(currentEntry.getContactId(),
		 * content); // contactListView.setAdapter(new
		 * ContactListViewAdapter(content,SelectContactActivity.this)); } }
		 * 
		 * });
		 */
		ratingBar = (RatingBar) findViewById(R.id.ratingBar1);	
		ratingBar.setOnRatingBarChangeListener(new OnRatingBarChangeListener() {
			@Override
			public void onRatingChanged(RatingBar ratingBar, float rating,
					boolean fromUser) {
				// String value;
				// txtRatingValue.setText(String.valueOf(rating));
				//Log.i("Select Contact Activity",String.valueOf(value));
				value = String.valueOf(rating);

			}
		});

		queryAllRawContacts();
		contactSpinner.setAdapter(adapter);
	}

	public void suggest(View view) {
		
		r = new RestService(mHandlerP, this,
				"http://jigar-btp.cloudapp.net/suggest_service/",
				RestService.POST);

		r.addParam("service_name", "maid");
		r.addParam("sp_name", cname);
		r.addParam("rating", value);
		r.addParam("contact", cnum);

		try {
			r.execute();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	// asdokoekokeokdoekdoekd
	private static final String TAG = "SelectContactActivity";
	private final Handler mHandlerP = new Handler() {
		@Override
		public void handleMessage(Message msg) {
			// t_query1.setText((String) msg.obj);
			String[] response;
			Log.i(TAG, ((String) msg.obj));
			response = ((String) msg.obj).split("\"");
			Log.i(TAG, response[3]);
			if (response[3].equals("1")) {
				Log.i(TAG, "WHy");
				Context context = getApplicationContext();
				CharSequence text = "Suggestion Sent to your neighbours";
				int duration = Toast.LENGTH_SHORT;
				Toast toast = Toast.makeText(context, text, duration);
				toast.show();

			} else {
				Context context = getApplicationContext();
				CharSequence text = "Sorry! Please retry";
				int duration = Toast.LENGTH_SHORT;
				Toast toast = Toast.makeText(context, text, duration);
				toast.show();
			}

		}

	};

	private void queryAllRawContacts() {

		final String[] projection = new String[] { RawContacts.CONTACT_ID, // the
																			// contact
																			// id
																			// column
				RawContacts.DELETED // column if this contact is deleted
		};

		final Cursor rawContacts = managedQuery(RawContacts.CONTENT_URI, // the
																			// uri
																			// for
																			// raw
																			// contact
																			// provider
				projection, null, // selection = null, retrieve all entries
				null, // not required because selection does not contain
						// parameters
				null); // do not order

		final int contactIdColumnIndex = rawContacts
				.getColumnIndex(RawContacts.CONTACT_ID);
		final int deletedColumnIndex = rawContacts
				.getColumnIndex(RawContacts.DELETED);

		spinnerContent.clear();
		if (rawContacts.moveToFirst()) { // move the cursor to the first entry
			while (!rawContacts.isAfterLast()) { // still a valid entry left?
				final int contactId = rawContacts.getInt(contactIdColumnIndex);
				final boolean deleted = (rawContacts.getInt(deletedColumnIndex) == 1);
				if (!deleted) {
					spinnerContent
							.add(queryDetailsForContactSpinnerEntry(contactId));
				}
				rawContacts.moveToNext(); // move to the next entry
			}
		}

		rawContacts.close();
	}

	private SpinnerEntry queryDetailsForContactSpinnerEntry(int contactId) {
		final String[] projection = new String[] { Contacts.DISPLAY_NAME, // the
																			// name
																			// of
																			// the
																			// contact
				Contacts.PHOTO_ID // the id of the column in the data table for
									// the image
		};

		final Cursor contact = managedQuery(Contacts.CONTENT_URI, projection,
				BaseColumns._ID + "=?", // filter entries on the basis of the
										// contact id
				new String[] { String.valueOf(contactId) }, // the parameter to
															// which the contact
															// id column is
															// compared to
				null);

		if (contact.moveToFirst()) {
			final String name = contact.getString(contact
					.getColumnIndex(Contacts.DISPLAY_NAME));

			final String photoId = contact.getString(contact
					.getColumnIndex(Contacts.PHOTO_ID));
			final Bitmap photo;
			if (photoId != null) {
				photo = queryContactBitmap(photoId);
			} else {
				photo = null;
			}
			contact.close();
			return new SpinnerEntry(contactId, photo, name);
		}
		contact.close();

		return null;
	}

	public int getName(String name) {
		cname = name;
		return 1;
	}

	private Bitmap queryContactBitmap(String photoId) {
		final Cursor photo = managedQuery(Data.CONTENT_URI,
				new String[] { Photo.PHOTO }, // column where the blob is stored
				BaseColumns._ID + "=?", // select row by id
				new String[] { photoId }, // filter by the given photoId
				null);

		final Bitmap photoBitmap;
		if (photo.moveToFirst()) {
			byte[] photoBlob = photo.getBlob(photo.getColumnIndex(Photo.PHOTO));
			photoBitmap = BitmapFactory.decodeByteArray(photoBlob, 0,
					photoBlob.length);
		} else {
			photoBitmap = null;
		}
		photo.close();
		return photoBitmap;
	}

	public void queryAllPhoneNumbersForContact(int contactId,
			List<ListViewEntry> content) {
		final String[] projection = new String[] { Phone.NUMBER, Phone.TYPE, };

		final Cursor phone = managedQuery(Phone.CONTENT_URI, projection,
				Data.CONTACT_ID + "=?",
				new String[] { String.valueOf(contactId) }, null);

		if (phone.moveToFirst()) {
			final int contactNumberColumnIndex = phone
					.getColumnIndex(Phone.NUMBER);
			final int contactTypeColumnIndex = phone.getColumnIndex(Phone.TYPE);

			// while(!phone.isAfterLast()) {
			final String number = phone.getString(contactNumberColumnIndex);
			int b = getNumber(number);
			final int type = phone.getInt(contactTypeColumnIndex);
			content.add(new ListViewEntry(number, Phone
					.getTypeLabelResource(type), R.string.type_phone));
			// phone.moveToNext();
			// }

		}
		phone.close();
	}

	

	public int getNumber(String num) {
		cnum = num;
		return 1;
	}

	public void queryAllEmailAddressesForContact(int contactId,
			List<ListViewEntry> content) {
		final String[] projection = new String[] { Email.DATA, // use
																// Email.ADDRESS
																// for API-Level
																// 11+
				Email.TYPE };

		final Cursor email = managedQuery(Email.CONTENT_URI, projection,
				Data.CONTACT_ID + "=?",
				new String[] { String.valueOf(contactId) }, null);

		if (email.moveToFirst()) {
			final int contactEmailColumnIndex = email
					.getColumnIndex(Email.DATA);
			final int contactTypeColumnIndex = email.getColumnIndex(Email.TYPE);

			while (!email.isAfterLast()) {
				final String address = email.getString(contactEmailColumnIndex);
				final int type = email.getInt(contactTypeColumnIndex);
				content.add(new ListViewEntry(address, Email
						.getTypeLabelResource(type), R.string.type_email));
				email.moveToNext();
			}

		}
		email.close();
	}

	

	public void addListenerOnRatingBar() {

		RatingBar ratingBar = (RatingBar) findViewById(R.id.ratingBar1);
		//txtRatingValue = (TextView) findViewById(R.id.txtRatingValue);

		// if rating value is changed,
		// display the current rating value in the result (textview)
		// automatically
		ratingBar.setOnRatingBarChangeListener(new OnRatingBarChangeListener() {
			@Override
			public void onRatingChanged(RatingBar ratingBar, float rating,
					boolean fromUser) {
				// String value;
				// txtRatingValue.setText(String.valueOf(rating));
				Log.i("Select Contact Activity",String.valueOf(value));
				value = String.valueOf(rating);

			}
		});
	}
}
