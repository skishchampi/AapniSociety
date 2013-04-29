package com.apdisociety;

import java.util.ArrayList;
import java.util.Timer;
import java.util.TimerTask;

//import TimerDemo.RemindTask;
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
import java.util.*;

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
func();

Log.i(TAG,"asd");


}

//***********************************************


Timer timer;

    public void func() {
     Log.i(TAG,"func called");
        timer = new Timer();
        timer.scheduleAtFixedRate(new RemindTask(),0,10000);
}

    class RemindTask extends TimerTask {
        public void run() {
            //GossipActivity act=new GossipActivity();
            GossipActivity.this.getGossip();
         // timer.cancel(); //Terminate the timer thread
        }
    }


//************************************************
public void getGossip(View view){
// tv = (TextView) findViewById(R.id.messageHistory);
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
// tv = (TextView) findViewById(R.id.messageHistory);
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

public static String[] array=new String[30];
public static ArrayList<String> list=new ArrayList<String>();
public static String[] array2=new String[6];
// public static String[] array2=new String[100];

private final Handler mHandlerPostR = new Handler(){
     @Override
     public void handleMessage(Message msg){
    
     display_string((String) msg.obj);
     }	
    };
    
    public void display_string(String s)
    {
     //tv.setText((String) msg.obj);
    	array = s.split(",");
    	display();
    }
    public void display(){
     int i=0;
     for(i=0;i<(array.length) - 1 ;i++){
    	 Log.i(TAG,array[i]);
    	 if (array[i].contains("\"")){	
    		 String str1="Anon:";
    		 array[i]=str1+array[i].split("\"")[1];	
}
}
     ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, R.layout.list_messages, array);	

     ListView listView = (ListView) findViewById(R.id.messageHistory);
     listView.setAdapter(adapter);
    // Log.i(TAG,"asd");
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