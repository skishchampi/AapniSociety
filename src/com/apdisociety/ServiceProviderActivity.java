package com.apdisociety;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SmsManager;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;
 
public class ServiceProviderActivity extends Activity implements OnItemClickListener{
    
	/** Called when the activity is first created. */
    
	String[] val = {"9879013521","8905057541","9510965329","97125591","9510965416","9510944138","9904980877"};
    
	ListView list;
    
	Dialog listDialog;
    
	@Override
    
	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        showdialog();
        (Toast.makeText(getApplicationContext(), getIntent().getExtras().getString("type"), Toast.LENGTH_LONG)).show();
        
    }
 
    private void showdialog()
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
         
    }
 
    @Override
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
    
    
    
}