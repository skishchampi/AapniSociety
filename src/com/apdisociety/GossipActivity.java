package com.apdisociety;

import android.annotation.TargetApi;
import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

public class GossipActivity extends Activity {
    
	RestService restServicePostS, restServicePostR;
	EditText send;
	TextView tv;
	private static final String TAG = "GossipActivity";
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		
		Log.i(TAG,"asd");
		
		super.onCreate(savedInstanceState);
		Log.i(TAG,"asd");
		setContentView(R.layout.activity_gossip);
		Log.i(TAG,"asd");
		// Show the Up button in the action bar.
		setupActionBar();
		Log.i(TAG,"asd");

		
		Log.i(TAG,"asd");
	}
	
	public void getGossip(View view){
		 tv  = (TextView) findViewById(R.id.messageHistory);
		Log.i(TAG,"asd");
		restServicePostR = new RestService(mHandlerPostR,this, "http://jigar-btp.cloudapp.net/gossip_receive/", RestService.POST);
		Log.i(TAG,"asd");
		try{
			Log.i(TAG,"asd");
			restServicePostR.execute();
			Log.i(TAG,"asd");
		}
		catch(Exception e){
			Log.i(TAG,"asd");
			e.printStackTrace();
			Log.i(TAG,"asd");
			
		}
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
		getMenuInflater().inflate(R.menu.gossip, menu);
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


	private final Handler mHandlerPostR = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			tv.setText((String) msg.obj);
    			Log.i(TAG,"asd");
    		}	
    };
	
	
	
	
	
    
    
	
}