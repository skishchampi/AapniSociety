package com.apdisociety;

import android.annotation.TargetApi;
import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.NavUtils;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class GossipActivity extends Activity {
    
	TextView tv  = (TextView) findViewById(R.id.messageHistory);
	RestService restServicePostR, restServicePostS;
	EditText send;

    
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_gossip);
		// Show the Up button in the action bar.
		setupActionBar();
		getGossip();
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
}

	public void getGossip() {
        restServicePostR = new RestService(mHandlerPostR, this, "http://jigar-btp.cloudapp.net/gossip_receive/", RestService.POST); //Create new rest service for post
        try {
     	   
			restServicePostR.execute(); //HTTP POSTing to the server
			
		} catch (Exception e) {
			e.printStackTrace();
		}    
	
	
	
	private final Handler mHandlerPostR = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			tv.setText((String) msg.obj);
    		}		
    };
    
    Button button = (Button) findViewById(R.id.sendMessageButton);
	button.setOnClickListener(new View.OnClickListener(){
		public void onClick(View view){
			try {
				restServicePostS.execute(); //Executes the request with the HTTP GET verb
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	});
	
}