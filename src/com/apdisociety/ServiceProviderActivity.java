package com.apdisociety;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.AdapterView.OnItemClickListener;
 
public class ServiceProviderActivity extends Activity implements OnItemClickListener{
    /** Called when the activity is first created. */
    String[] val = {"sunday","monday","tuesday","thrusday","friday","wednesday","march"};
    ListView list;
    Dialog listDialog;
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
         showdialog();
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
 
    public void onItemClick(AdapterView<?> arg0, View arg1, int arg2, long arg3)
    {
 
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("Delete item "+arg2)
                   .setPositiveButton("OK ", new DialogInterface.OnClickListener() {
                   public void onClick(DialogInterface dialog, int id) {
                       System.out.println("OK CLICKED");
 
                   }
               });
        builder.setNegativeButton("cancel", new DialogInterface.OnClickListener() {
               public void onClick(DialogInterface dialog, int id) {
                 dialog.dismiss();
                 listDialog.cancel();
 
               }
           });
 
        AlertDialog alert = builder.create();
        alert.setTitle("Information");
        alert.show();
    }
}