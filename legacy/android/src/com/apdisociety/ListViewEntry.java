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

public class ListViewEntry {

	/** The destination of the entry e.g. a phone number or email address **/
	private final String destinationAddress;

	/** String resource describing the type of the entry e.g. Home **/
	private final int typeResource;

	/** String resource which is used as a label for the entry **/
	private final int entryLabelResource;

	public ListViewEntry(String number, int typeResource,
			int entryLabelResource) {
		this.destinationAddress = number;
		this.typeResource = typeResource;
		this.entryLabelResource = entryLabelResource;
	}

	public String getDestinationAddress() {
		return destinationAddress;
	}

	public int getTypeResource() {
		return typeResource;
	}

	public int getEntryLabelResource() {
		return entryLabelResource;
	}

}
