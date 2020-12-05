#!/bin/sh
javac -cp ".:./jars/bcpkix-jdk15on-167.jar:./jars/bcprov-ext-jdk15to18-167.jar" PKI.java && java -cp ".:./jars/bcpkix-jdk15on-167.jar:./jars/bcprov-ext-jdk15to18-167.jar" PKI
