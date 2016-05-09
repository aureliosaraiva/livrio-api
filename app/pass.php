<?php
$password = $argv[1];
$passwordStorage = $argv[2];
echo password_verify($password,$passwordStorage)?'S':'N';