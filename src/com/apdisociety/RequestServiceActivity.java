package com.apdisociety;

import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.NavUtils;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Spinner;

public class RequestServiceActivity extends Activity {

	//RestService r;
	//private static final String TAG = "RequestServiceActivity";
	Spinner spinner;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_request_service);
		// Show the Up button in the action bar.
		setupActionBar();
		addListenerOnSpinnerItemSelection();
		

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
		getMenuInflater().inflate(R.menu.request, menu);
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
	
	public void addListenerOnSpinnerItemSelection() {
		spinner = (Spinner) findViewById(R.id.services); 
		spinner.setOnItemSelectedListener(new CustomOnItemSelectedListener());
	  }
	
	public void sendRequest (View view){
		 
	    
	    String type = String.valueOf(spinner.getSelectedItem());
		Intent intent = new Intent(this, ServiceProviderActivity.class);
		intent.putExtra("type", type);
		startActivity(intent);
	}
	
	/*public void sendRequest(View view){
		
		
		r = new RestService(mHandlerR, this, "http://jigar-btp.cloudapp.net/service_request/", RestService.POST);
    	r.addParam("service_name",String.valueOf(spinner.getSelectedItem()));
    	try{
    		r.execute();
    	}
    	catch (Exception e) {
    		e.printStackTrace();
    	}
		
		//Intent intent = new Intent(this, ServiceProviderActivity.class);
		//startActivity(intent);
	}
	
	private final Handler mHandlerR = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			//tv.setText((String) msg.obj);
    	//		array = ((String)msg.obj).split("\"");
    			/*for(int i =0;i < array.length; i++ ){
    				tv.setText(array[i]);
    			}*/
    			//Integer len=array.length;
    			//Log.i(TAG,len.toString());
    		//	int i=0;
    			//while(i!=array.length-1)
    			//{	
    				//if(i%2==1)
    				//{	
    					//int j=(i+1)/2;
    					//array2[j]=array[i];
    				//}
    				//i++;
    			//}
    			//i=0;
    			//display(array2);
    /*		
    		Context context = getApplicationContext();
			CharSequence text = (String) msg.obj;
			int duration = Toast.LENGTH_LONG;
			Toast toast = Toast.makeText(context, text, duration);
			toast.show();
    		}	
    };
	
	
	
	*/
}
