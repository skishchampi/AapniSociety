package com.apdisociety;

import java.util.Calendar;

import org.json.JSONException;
import org.json.JSONObject;

import android.annotation.TargetApi;
import android.app.DatePickerDialog;
import android.app.Dialog;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.DialogFragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.RadioButton;

public class SignupActivity extends FragmentActivity {

	RestService restServicePost;
	private static final String TAG = "MyActivity";
	public static String[] response;
	
	public static class DatePickerFragment extends DialogFragment
    implements DatePickerDialog.OnDateSetListener {

	@Override
	public Dialog onCreateDialog(Bundle savedInstanceState) {
	// Use the current date as the default date in the picker
	final Calendar c = Calendar.getInstance();
	int year = c.get(Calendar.YEAR);
	int month = c.get(Calendar.MONTH);
	int day = c.get(Calendar.DAY_OF_MONTH);

	// Create a new instance of DatePickerDialog and return it
	return new DatePickerDialog(getActivity(), this, year, month, day);
	}

	public void onDateSet(DatePicker view, int year, int month, int day) {
	// Do something with the date chosen by the user
	}
	
	
}
	private static final String LOG_TAG = null;
	public void showDatePickerDialog(View v) {
	    DialogFragment newFragment = new DatePickerFragment();
	    newFragment.show(getSupportFragmentManager(), "datePicker");
	}
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_signup);
		restServicePost = new RestService(mHandlerP, this, "http://jigar-btp.cloudapp.net/register/", RestService.POST); //Create new rest service for post
		// Show the Up button in the action bar.
		setupActionBar();
		System.out.print("askn");
	}

	/**
	 * Set up the {@link android.app.ActionBar}, if the API is available.
	 */
	@TargetApi(Build.VERSION_CODES.HONEYCOMB)
	private void setupActionBar() {
		if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB) {
			getActionBar().setDisplayHomeAsUpEnabled(true);
		}
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.signup, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case android.R.id.home:
			// This ID represents the Home or Up button. In the case of this
			// activity, the Up button is shown. Use NavUtils to allow users
			// to navigate up one level in the application structure. For
			// more details, see the Navigation pattern on Android Design:
			//
			// http://developer.android.com/design/patterns/navigation.html#up-vs-back
			//
			NavUtils.navigateUpFromSameTask(this);
			return true;
		}
		return super.onOptionsItemSelected(item);
	}
	
	public static String mf;
	
	/*Button signUp = (Button) findViewById(R.id.button1);
	signUp.setOnClickListener(new View.OnClickListener(){
		public void onClick(View view){
			try {
				restServicePost.execute(); //Executes the request with the HTTP Posting
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}); */
	
	public void signUp(View view) {
	  EditText fname = (EditText)findViewById(R.id.editText1);
	  EditText lname = (EditText)findViewById(R.id.editText5);
	  EditText mail1 = (EditText)findViewById(R.id.editText2);
	  EditText mail2 = (EditText)findViewById(R.id.editText3);
	  EditText pwd = (EditText)findViewById(R.id.editText4);
	  
	  String email = mail1.getText().toString();
	  
	  System.out.print(fname.getText().toString());
	  Log.i(TAG, fname.getText().toString());
	  System.out.print(pwd.getText().toString());
	  System.out.print(email);
	  
	  
      restServicePost.addParam("username", fname.getText().toString()); //Add params to request
      restServicePost.addParam("password",pwd.getText().toString()); //Format for a typical form encoded nested attribute
      restServicePost.addParam("email",email);
      
      
      try {
    	   
			restServicePost.execute(); //HTTP POSTing to the server
		} catch (Exception e) {
			e.printStackTrace();
		}    
	}
    
	private final Handler mHandlerP = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			//t_query1.setText((String) msg.obj);
    		Log.i(TAG,((String)msg.obj));
    		response = ((String)msg.obj).split("\"");
    		Log.i(TAG,response[3]);
    		
    		
    		}		
    };
public void onRadioButtonClicked(View view) {
	    // Is the button now checked?
	    boolean checked = ((RadioButton)view).isChecked();
	    
	    // Check which radio button was clicked
	    switch(view.getId()) {
	        case R.id.radioMale:
	            if (checked)
	                mf = "male" ;
	            break;
	        case R.id.radioFemale:
	            if (checked)
	                mf = "female";
	            break;
	    }
	}
}
