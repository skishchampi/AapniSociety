package com.apdisociety;

import java.util.ArrayList;

import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

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
		// tv  = (TextView) findViewById(R.id.messageHistory);
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
	public void getGossip(){
		// tv  = (TextView) findViewById(R.id.messageHistory);
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
    public void sendGossip(View view){
    	send = (EditText) findViewById(R.id.message);
    	restServicePostS = new RestService(mHandlerPostS, this, "http://jigar-btp.cloudapp.net/gossip_enter/", RestService.POST);
    	restServicePostS.addParam("chat", send.getText().toString());
    	try{
    		restServicePostS.execute();
    	}
    	catch (Exception e) {
    		e.printStackTrace();
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

    public static String[] array;
    public static String[] array2=new String[100];
    
    public static ArrayList<String> str=new ArrayList<String>();
	
	private final Handler mHandlerPostR = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			//tv.setText((String) msg.obj);
    			array = ((String)msg.obj).split("\"");
    			/*for(int i =0;i < array.length; i++ ){
    				tv.setText(array[i]);
    			}*/
    			//Integer len=array.length;
    			//Log.i(TAG,len.toString());
    			/*int i=0;
    			while(i!=array.length-1)
    			{	
    				if(i%2==1)
    				{	
    					int j=(i+1)/2;
    					array2[j]=array[i];
    				}
    				i++;
    			}
    			i=0; */
    			display(array);
    		}	
    };
    
    public void display(String[] array3){
    	ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, R.layout.list_messages, array3);			
		
		ListView listView = (ListView) findViewById(R.id.messageHistory);
		listView.setAdapter(adapter);
		Log.i(TAG,"asd");
    }
    
    public static String[] response;
    //Intent intent = new Intent(this,GossipActivity.class);
    
	private final Handler mHandlerPostS = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    			
    			Log.i(TAG,"asd");
    			Log.i(TAG,((String)msg.obj));
        		response = ((String)msg.obj).split("\"");
        		Log.i(TAG,response[3]);
        		if(response[3].equals("1")){
        		    Log.i(TAG, "WHy");
        		    getGossip();
        		    Context context = getApplicationContext();
        			CharSequence text = "Message sent";
        			int duration = Toast.LENGTH_SHORT;
        			Toast toast = Toast.makeText(context, text, duration);
        			toast.show();
        			send.setText("");
        			//tv.setText((String) msg.obj);
    				
    			}
        		else {
        			Context context = getApplicationContext();
        			CharSequence text = "Message couldn't be sent";
        			int duration = Toast.LENGTH_SHORT;
        			Toast toast = Toast.makeText(context, text, duration);
        			toast.show();
        		}
    		}	
    };
	
   
	
	
	
    
    
	
}