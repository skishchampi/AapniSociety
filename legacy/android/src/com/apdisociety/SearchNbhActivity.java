package com.apdisociety;

import java.util.ArrayList;
import java.util.HashMap;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.annotation.TargetApi;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.NavUtils;
import android.telephony.SmsManager;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.SimpleAdapter;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

public class SearchNbhActivity extends FragmentActivity {
	
	private GoogleMap mMap;
    RestService r; 
    
    private static final String TAG_PLACES = "places";
	private static final String TAG_PLON = "plon";
	private static final String TAG_PLAT = "plat";
	private static final String TAG_NAME = "name";
	private static final String TAG_SUG = "suggestedby";
	JSONArray places = null;
	
	ArrayList<HashMap<String, String>> placesList = new ArrayList<HashMap<String, String>>();

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_search_nbh);
		
		    r= new RestService(mHandlerP, this, "http://jigar-btp.cloudapp.net/request_places/", RestService.POST);
	        r.addParam("type", getIntent().getExtras().getString("type"));
	        try{
	        	
	        	r.execute();
	        	
	        	
	        }catch(Exception e){
	        	e.printStackTrace();
	        }
	        
		
		// Show the Up button in the action bar.
	    //setUpMapIfNeeded();
		setupActionBar();
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
            places = json.getJSONArray(TAG_PLACES);
             Log.i("CSAALL","HUA");
            // looping through All Contacts
            for(int i = 0; i < places.length(); i++){
                JSONObject c = places.getJSONObject(i);
                 
                // Storing each json item in variable
                
                String name = c.getString(TAG_NAME);
                String plat = c.getString(TAG_PLAT);
                String plon = c.getString(TAG_PLON);
                String sby = c.getString(TAG_SUG);
                
                String mtext = name + sby; 
                
                double lat=Double.valueOf(plat);
                double lon=Double.valueOf(plon);
                
    //           setUpMap(lat, lon, mtext);
                //mMap.addMarker(new MarkerOptions().position(new LatLng(Double.valueOf(plat), Double.valueOf(plon))).title(mtext));
                
                
                
                //String message=name+ "\n" +phone + "\n" + rating; 
         
            /*     
                // creating new HashMap
                HashMap<String, String> map = new HashMap<String, String>();
                 
                // adding each child node to HashMap key => value
              //  map.put(TAG_NAME, name);
                map.put(TAG_NAME, name);
                map.put(TAG_PLAT, plat);
                map.put(TAG_PLON, plon);
                map.put(TAG_SUG, sby);
                
               // map.put(TAG_RATING, rating);
         
 
                // adding HashList to ArrayList
                placesList.add(map); */
            }
        } catch (JSONException e) {
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
		getMenuInflater().inflate(R.menu.search_nbh, menu);
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

	
	 /*private void setUpMapIfNeeded() {
	        // Do a null check to confirm that we have not already instantiated the map.
	        if (mMap == null) {
	            // Try to obtain the map from the SupportMapFragment.
	            mMap = ((SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.map))
	                    .getMap();
	            // Check if we were successful in obtaining the map.
	            if (mMap != null) {
	                setUpMap();
	            }
	        }
	    }*/

	    @Override
	    protected void onResume() {
	        super.onResume();
	  //     setUpMapIfNeeded();
	    }
	    
	    /**
	     * This is where we can add markers or lines, add listeners or move the camera. In this case, we
	     * just add a marker near Africa.
	     * <p>
	     * This should only be called once and when we are sure that {@link #mMap} is not null.
	     */
	    
	    private void setUpMap(double a, double b, String c) {
	    	
	        mMap.addMarker(new MarkerOptions().position(new LatLng(a, b)).title(c));
	    }
	
}
