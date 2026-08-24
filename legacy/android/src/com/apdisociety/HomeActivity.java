package com.apdisociety;


import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

public class HomeActivity extends Activity {
	
	RestService restServicePost;
	private static final String TAG = "SignInActivity";
	public Intent intent;
	public static String[] response;
	SessionManager session;
	
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_home);
		// Show the Up button in the action bar.
		setupActionBar();
		
		session = new SessionManager(getApplicationContext());
		session.checkLogin();
		
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
		

		getMenuInflater().inflate(R.menu.home, menu);
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
	
	public void requestService(View view) {
	
		Intent intent = new Intent (this, SelectPeopleActivity.class);
		startActivity(intent);
	}
	
	public void neighbourhood(View view) {
		
		Intent intent = new Intent (this, NbhSelectActivity.class);
		startActivity(intent);
	}
    
	
    
	public void gossip(View view){
		Intent intent = new Intent(this, GossipActivity.class);
		startActivity(intent);
		
	}
  

	public void signOut(View view) {
		
		//EditText uname =  (EditText)findViewById(R.id.editText1);
		//EditText pwd =  (EditText)findViewById(R.id.editText2);
        restServicePost = new RestService(mHandlerP,this, "http://jigar-btp.cloudapp.net/logout/",RestService.POST);
		//restServicePost.addParam("username", uname.getText().toString());
	    //restServicePost.addParam("password",pwd.getText().toString());  
	    try {
	    	Log.i(TAG, "Fuck you");
			restServicePost.execute();
			Log.i(TAG, "Fuck you sucker");
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		
	}
	public void callback(String value){
		session.logoutUser();
		Intent  intent = new Intent(this, MainActivity.class);
		startActivity(intent);
	}
	
	private final Handler mHandlerP = new Handler(){
    	@Override
    	public void handleMessage(Message msg){
    		
    			//t_query1.setText((String) msg.obj);
    		Log.i(TAG,((String)msg.obj));
    		response = ((String)msg.obj).split("\"");
    		Log.i(TAG,response[3]);
    		if(response[3].equals("1")){
    		    Log.i(TAG, "WHy");	
				//startActivity(intent);
    		    (Toast.makeText(getApplicationContext(), "Signed you out", Toast.LENGTH_SHORT)).show();
    		    callback(response[3]);
			}else{
				(Toast.makeText(getApplicationContext(), "Couldn't Sign you out", Toast.LENGTH_SHORT)).show();
			} 
    		
    		
    	}
    		
	}; 
	
}
