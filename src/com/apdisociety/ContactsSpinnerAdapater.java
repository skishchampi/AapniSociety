/*
 * Copyright (c) 2011 APP-SOLUT
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

package com.apdisociety;

import java.util.List;

import android.app.Activity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.SpinnerAdapter;
import android.widget.TextView;

public class ContactsSpinnerAdapater extends BaseAdapter implements
		SpinnerAdapter {
	private final List<SpinnerEntry> content;
	private final Activity activity;

	public ContactsSpinnerAdapater(List<SpinnerEntry> content,
			Activity activity) {
		super();
		this.content = content;
		this.activity = activity;
	}

	public int getCount() {
		return content.size();
	}

	public SpinnerEntry getItem(int position) {
		return content.get(position);
	}

	public long getItemId(int position) {
		return position;
	}

	public View getView(int position, View convertView,
			ViewGroup parent) {
		final LayoutInflater inflater = activity.getLayoutInflater();	// default layout inflater
		final View spinnerEntry = inflater.inflate(
				R.layout.spinner_entry_with_icon, null);				// initialize the layout from xml
		final TextView contactName = (TextView) spinnerEntry
				.findViewById(R.id.spinnerEntryContactName);
		final ImageView contactImage = (ImageView) spinnerEntry
				.findViewById(R.id.spinnerEntryContactPhoto);
		final SpinnerEntry currentEntry = content.get(position);	
		contactName.setText(currentEntry.getContactName());
		contactImage.setImageBitmap(currentEntry.getContactPhoto());
		return spinnerEntry;
	}

}
