package com.apdisociety;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.View;
import android.widget.Spinner;

public class SearchNActivity extends Activity {
    
	Spinner spinner;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_search_n);
		addListenerOnSpinnerItemSelection();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.search_n, menu);
		return true;
	}
	
	public void gotoMap(View view){
		Intent intent = new Intent(this, SearchNbhActivity.class);
		intent.putExtra("type", String.valueOf(spinner.getSelectedItem()));
		startActivity(intent);
	}
	
	public void addListenerOnSpinnerItemSelection() {
		spinner = (Spinner) findViewById(R.id.spinner1);
		spinner.setOnItemSelectedListener(new CustomOnItemSelectedListener());
	  }

}
