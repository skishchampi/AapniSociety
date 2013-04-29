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

import android.graphics.Bitmap;

public class SpinnerEntry {

	/** The unique id of this contact as defined in the raw contact table **/
	private final int contactId;

	/** The picture of this contact - if available **/
	private final Bitmap contactPhoto;

	/** The name which should be displayed for this contact **/
	private final String contactName;

	public SpinnerEntry(int contactID, Bitmap contactPhoto,
			String contactName) {
		this.contactId = contactID;
		this.contactPhoto = contactPhoto;
		this.contactName = contactName;
	}

	public int getContactId() {
		return contactId;
	}

	public Bitmap getContactPhoto() {
		return contactPhoto;
	}

	public String getContactName() {
		return contactName;
	}

}
