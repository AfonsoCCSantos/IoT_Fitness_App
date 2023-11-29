"!/bin/bash"

echo " ------------------------------------------------------ "
echo "Creating CA key The passkey is important so remember it"
openssl genrsa -des3 -out ca.key 2048 

echo " ------------------------------------------------------ "
echo "Created CA Certificate 10 years expiry"
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt 

echo " ------------------------------------------------------ "
echo "Creating Server key"
openssl genrsa -out server.key 2048

echo " ------------------------------------------------------ "
echo "Creating Server certificate"
openssl req -new -out server.csr -key server.key

echo " ------------------------------------------------------ "
echo "Signing Server certificate Server certificate"
echo "Common Name should be the FQDN or IP address of the server"
echo "It is what you would use to ping the server"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 

echo " ------------------------------------------------------ "
echo "Creating Client Key"
openssl genrsa -out client.key 2048

echo " ------------------------------------------------------ "
echo "Creating certificate request"
openssl req -new -out client.csr -key client.key

echo " ------------------------------------------------------ "
echo "Signing client certificate with CA key"
echo "The CA key File must be in the server-certs folder"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365