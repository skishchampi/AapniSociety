package com.apdisociety;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.View;

public class SelectPeopleActivity extends Activity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_select_people);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.select_people, menu);
		return true;
	}

	public void suggest(View view){
		Intent intent = new Intent(this, SelectContactActivity.class);
		startActivity(intent);
	}
	
	public void request(View view){
		Intent intent = new Intent(this,RequestServiceActivity.class);
		startActivity(intent);
	}
}
