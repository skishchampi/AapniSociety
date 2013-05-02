package com.apdisociety;

import java.util.ArrayList;
import java.util.HashMap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Dialog;
import android.app.ListActivity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.SimpleAdapter;
import android.widget.TextView;
import android.widget.Toast;
 
public class ServiceProviderActivity extends ListActivity {
    
	/** Called when the activity is first created. */
    
	String[] val = {"9879013521","8905057541","9510965329","97125591","9510965416","9510944138","9904980877"};
    
	ListView list;
    
	Dialog listDialog;
	
	RestService r;
	
	private static final String TAG_CONTACTS = "contacts";
	private static final String TAG_NAME = "name";
	private static final String TAG_PHONE = "phone";
	private static final String TAG_RATING = "rating";
	JSONArray contacts = null;
	
	ArrayList<HashMap<String, String>> contactList = new ArrayList<HashMap<String, String>>();
    
	@Override
    
	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        r= new RestService(mHandlerP, this, "http://jigar-btp.cloudapp.net/service_request/", RestService.POST);
        r.addParam("service_name", getIntent().getExtras().getString("type"));
        try{
        	
        	r.execute();
        	
        	
        }catch(Exception e){
        	e.printStackTrace();
        }
        
        
        
        
       // showdialog();
//        (Toast.makeText(getApplicationContext(), getIntent().getExtras().getString("type"), Toast.LENGTH_LONG)).show();
        
        
        
    }
	
	
	private final Handler mHandlerP = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    		Log.e("Jigar",msg.obj.toString());
    			try {
					JSONObject j = new JSONObject((String)msg.obj);
					getJSON(j);
							         
				     
					
					
				} catch (JSONException e) {
					// TODO Auto-generated catch block
					Log.e("JSON Parser", "Error parsing data " + e.toString());
				}
    			 	
    			
    			
    		}	
    };
    
    public void getJSON(JSONObject json){
    	 try {
             // Getting Array of Contacts
             contacts = json.getJSONArray(TAG_CONTACTS);
              
             // looping through All Contacts
             for(int i = 0; i < contacts.length(); i++){
                 JSONObject c = contacts.getJSONObject(i);
                  
                 // Storing each json item in variable
                 
                 String name = c.getString(TAG_NAME);
                 String phone = c.getString(TAG_PHONE);
                 String rating = c.getString(TAG_RATING);
                 
                  
          
                  
                 // creating new HashMap
                 HashMap<String, String> map = new HashMap<String, String>();
                  
                 // adding each child node to HashMap key => value
               //  map.put(TAG_NAME, name);
                 map.put(TAG_PHONE, phone);
                // map.put(TAG_RATING, rating);
          
  
                 // adding HashList to ArrayList
                 contactList.add(map);
             }
         } catch (JSONException e) {
             e.printStackTrace();
         }
    	// LayoutInflater li = (LayoutInflater) this.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
         // View v = li.inflate(R.layout.activity_service_provider, null, false);
         
         //listDialog.setContentView(v);
    	 
    	 ListAdapter adapter = new SimpleAdapter(this, contactList,R.layout.activity_service_provider,new String[] {  TAG_PHONE }, new int[] {R.id.phone });
  
         setListAdapter(adapter);
  
         // selecting single ListView item
         ListView lv = getListView();
           
         // Launching new screen on Selecting Single ListItem
         lv.setOnItemClickListener(new OnItemClickListener() {
  
             @Override
             public void onItemClick(AdapterView<?> parent, View view,
                     int position, long id) {
                 // getting values from selected ListItem
         //        String name = ((TextView) view.findViewById(R.id.name)).getText().toString();
                 String phone = ((TextView) view.findViewById(R.id.phone)).getText().toString();
           //      String rating = ((TextView) view.findViewById(R.id.rating)).getText().toString();
                  
                 String sms = "Help required, Please reach me out asap";
                 
                 try {
                	if(phone.length() != 10) { 
          			SmsManager smsManager = SmsManager.getDefault();
          			smsManager.sendTextMessage(phone, null, sms, null, null);
          			Toast.makeText(getApplicationContext(), "SMS Sent!",
          						Toast.LENGTH_LONG).show();
                	}else {
                		Toast.makeText(getApplicationContext(), "No Phone Number Found, Sorry!",
          						Toast.LENGTH_LONG).show();
                	}
                		
                	
          		  } catch (Exception e) {
          			Toast.makeText(getApplicationContext(),
          				"SMS failed, please try again later!",
          				Toast.LENGTH_LONG).show();
          			e.printStackTrace();
          		  }
               /*  // Starting new intent
                 Intent in = new Intent(getApplicationContext(), SingleMenuItemActivity.class);
                 in.putExtra(TAG_NAME, name);
                 in.putExtra(TAG_EMAIL, cost);
                 in.putExtra(TAG_PHONE_MOBILE, description);
                 startActivity(in); */
             }
         });
    	 
    	
    }
    
    
 /*   private void showdialog()
    {
        listDialog = new Dialog(this);
        listDialog.setTitle("Available People");
      
        LayoutInflater li = (LayoutInflater) this.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        View v = li.inflate(R.layout.activity_service_provider, null, false);
        
        listDialog.setContentView(v);
        listDialog.setCancelable(true);
         //there are a lot of settings, for dialog, check them all out!
 
         ListView list1 = (ListView) listDialog.findViewById(R.id.listview);
         list1.setOnItemClickListener(this);
         list1.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_list_item_1, val));
         //now that the dialog is set up, it's time to show it
         listDialog.show();
         
    } */
 
    /*@Override
	public void onItemClick(AdapterView<?> arg0, View arg1, int arg2, long arg3)
    {
       
       String phone = arg0.getItemAtPosition(arg2).toString();
       String sms = "Help required, Please reach me out asap";
       
       try {
			SmsManager smsManager = SmsManager.getDefault();
			smsManager.sendTextMessage(phone, null, sms, null, null);
			Toast.makeText(getApplicationContext(), "SMS Sent!",
						Toast.LENGTH_LONG).show();
		  } catch (Exception e) {
			Toast.makeText(getApplicationContext(),
				"SMS failed, please try again later!",
				Toast.LENGTH_LONG).show();
			e.printStackTrace();
		  }
       */
    	
     /*  AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("Delete item "+arg2)
                   .setPositiveButton("OK ", new DialogInterface.OnClickListener() {
                   @Override
				public void onClick(DialogInterface dialog, int id) {
                       System.out.println("OK CLICKED");
 
                   }
               });
        builder.setNegativeButton("cancel", new DialogInterface.OnClickListener() {
               @Override
			public void onClick(DialogInterface dialog, int id) {
                 dialog.dismiss();
                 listDialog.cancel();
 
               }
           });
 
        AlertDialog alert = builder.create();
        alert.setTitle("Information");
        alert.show(); */ 
        }
    
    
    
