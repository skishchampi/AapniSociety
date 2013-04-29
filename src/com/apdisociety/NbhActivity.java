package com.apdisociety;

import android.annotation.TargetApi;
import android.app.Activity;
import android.app.Dialog;
import android.app.ProgressDialog;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.ConnectivityManager;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.app.NavUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

public class NbhActivity extends Activity {
    private String pname;
    private String ptype;
    private double plat;
    private double plon;
    int flag=0;
    
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_nbh);
		// Show the Up button in the action bar.
		if(!isOnline()){
			Toast.makeText(getApplicationContext(), "Please enable GPS", 5).show();
		}
		
		setupActionBar();
		
		 LocationManager locationManager = (LocationManager) this.getSystemService(Context.LOCATION_SERVICE);
         // Define a listener that responds to location updates
   LocationListener locationListener = new LocationListener() {
 
   	public void onLocationChanged(Location location) {
         // Called when a new location is found by the network location provider.
   		makeUseOfNewLocation(location);
       }
       public void onStatusChanged(String provider, int status, Bundle extras) {}

       public void onProviderEnabled(String provider) {}

       public void onProviderDisabled(String provider) {
       }
     };

   // Register the listener with the Location Manager to receive location updates
   locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 0, 0, locationListener);
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
		getMenuInflater().inflate(R.menu.nbh, menu);
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
    
	public void addLocation(View view){
		pname = ((EditText)findViewById(R.id.editText1)).getText().toString();
		ptype = String.valueOf(((Spinner)findViewById(R.id.spinner1)).getSelectedItem());
		
		if(pname.length()==0){
			Toast toast = Toast.makeText(view.getContext(),"Enter Name of place", Toast.LENGTH_SHORT);
    	    toast.show();
			
		}else if(ptype.length() == 0){
			Toast toast = Toast.makeText(view.getContext(),"Select type of place", Toast.LENGTH_SHORT);
    	    toast.show();
			
		}else {
		   Log.e("Latitude NIMS",Double.toString(plat));
      	   Log.e("Longitude NIMS",Double.toString(plon));
      	   if(isOnline()==false)
		   	    {
		   	    	Toast toast = Toast.makeText(view.getContext(),"Your internet is not connected.First connect the internet and then try again.", Toast.LENGTH_SHORT);
	        		toast.show();
		   	    }
		   	    else
		   	    {
          	   showDialog(3);
			       new Thread(new Runnable(){
			    			public void run(){
			    				if(flag==1)
			    				{    
			    					dismissDialog(3);
			    				
			    				}
			    			}
			    			}).start();
          	   
		   	    }
		}
		
		
	}
	 protected Dialog onCreateDialog(int id) {
	     if(id == 3){
	             ProgressDialog loadingDialog = new ProgressDialog(this);
	             loadingDialog.setMessage("Fetching Location and keep moving...");
	             loadingDialog.setIndeterminate(true);
	             loadingDialog.setCancelable(true);
	             return loadingDialog;
	     }
	     return super.onCreateDialog(id);
	    }
	protected void  makeUseOfNewLocation(Location location) {
		flag=1;
	    plat=location.getLatitude();
	    plon=location.getLongitude();		
	} 
	
	public boolean isOnline() {
        ConnectivityManager conMgr =
            (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (conMgr.getActiveNetworkInfo() != null && conMgr.getActiveNetworkInfo().isAvailable() &&    conMgr.getActiveNetworkInfo().isConnected()) {
            return true;
      } else {
            System.out.println("Internet Connection Not Present");
          return false;
      }
    }
}
