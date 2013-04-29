package com.apdisociety;

import org.apache.http.client.HttpClient;
import org.apache.http.impl.client.DefaultHttpClient;

import android.app.Application;

public class Client extends Application {

    public static HttpClient client = new DefaultHttpClient();


}
