# tcpforwarding

Crear archivo 'openssl.cnf'
```bash
[ req ]
default_bits = 2048
distinguished_name = req_distinguished_name
req_extensions = req_ext

[ req_distinguished_name ]
countryName = Country Name (2 letter code)
countryName_default = US
stateOrProvinceName = State or Province Name (full name)
stateOrProvinceName_default = CA
localityName = Locality Name (eg, city)
localityName_default = City
organizationalUnitName = Organizational Unit Name (eg, section)
organizationalUnitName_default = Unit
commonName = Common Name (eg, fully qualified host name)
commonName_default = localhost

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
IP.1 = 127.0.0.1
IP.2 = 192.168.0.15
IP.3 = 192.168.0.26
IP.4 = 192.168.0.109
```

- x.109 host_a
- x.15 host_b
- x.26 host_c

```bash
openssl genpkey -algorithm RSA -out key.pem
openssl req -new -x509 -key key.pem -out cert.pem -days 365 -config openssl.cnf
```
