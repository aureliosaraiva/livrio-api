#!/bin/sh


createTunnel() {
    /usr/bin/ssh -f -N  -L 4454:localhost:4455 tunnel@db01.codeway.in -p 2144
    if [ $? -eq 0 ]; then
        echo "Tunnel to db02 created successfully" | mail -s "[MONGO-TUNNEL]" aurelio@codeway.com.br
        echo Tunnel to $REMOTEHOST created successfully
    else
        echo "An error occurred creating a tunnel to db02 RC was $?" | mail -s "[MONGO-TUNNEL]" aurelio@codeway.com.br
        echo An error occurred creating a tunnel to $REMOTEHOST RC was $?
    fi
}

## Run the 'ls' command remotely.  If it returns non-zero, then create a new connection
/usr/bin/ssh -p 4454 tunnel@db01.codeway.in -p 2144 ls >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo Creating new tunnel connection
    createTunnel
fi
