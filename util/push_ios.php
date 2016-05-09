<?php

$token = $argv[1];
$message = base64_decode($argv[2]);

$path = getcwd();
$cert = $path . '/settings/ssl/apns/ckp.pem';
try{
    $ctx = stream_context_create();
    stream_context_set_option($ctx, 'ssl', 'local_cert', $cert);
    stream_context_set_option($ctx, 'ssl', 'passphrase', 'Z4vMkyltu');

    // Open a connection to the APNS server
    $fp = stream_socket_client(
        'ssl://gateway.push.apple.com:2195', $err,
        $errstr, 60, STREAM_CLIENT_CONNECT|STREAM_CLIENT_PERSISTENT, $ctx);

    if (!$fp){
        return false;
    }

    // Create the payload body
    $body['aps'] = array(
        'alert' => $message,
        'content-available' => 1
    );

    // Encode the payload as JSON
    $payload = json_encode($body);

    // Build the binary notification
    $msg = chr(0) . pack('n', 32) . pack('H*', $token) . pack('n', strlen($payload)) . $payload;

    // Send it to the server
    fwrite($fp, $msg, strlen($msg));
    echo 'S';
}
catch(\Exception $e){
    echo 'N';
}
