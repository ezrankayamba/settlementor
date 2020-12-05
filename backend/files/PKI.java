import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.security.*;
import java.security.spec.*;
import java.security.interfaces.*;
import java.nio.charset.*;
import javax.xml.bind.DatatypeConverter;

import java.nio.file.Files;
import java.nio.file.Path;

import org.bouncycastle.cert.*;
import org.bouncycastle.cert.jcajce.*;
import org.bouncycastle.cms.jcajce.*;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.operator.ContentSigner;
import org.bouncycastle.operator.jcajce.*;
import org.bouncycastle.util.Store;
import org.bouncycastle.util.encoders.*;
import org.bouncycastle.openssl.*;
import org.bouncycastle.util.io.pem.*;

class PKI {
	public static void main(String args[]) throws Exception{
		Security.addProvider(new BouncyCastleProvider());

		File f = new File("public_key.pem");
    		/*FileInputStream fis = new FileInputStream(f);
    		DataInputStream dis = new DataInputStream(fis);
    		byte[] keyBytes = new byte[(int)f.length()];
    		dis.readFully(keyBytes);
    		dis.close();

		X509EncodedKeySpec spec = new X509EncodedKeySpec(keyBytes);
	    	KeyFactory kf = KeyFactory.getInstance("RSA");
		PublicKey publicKey = kf.generatePublic(spec);*/
		PublicKey publicKey = readPublicKey(f);
		System.out.println("Public Success");

		Signature signature = Signature.getInstance("SHA256WithRSA/PSS");
		signature.initVerify(publicKey);

		String raw = new String(Files.readAllBytes(Paths.get("test.csv")));
		System.out.println(raw);
		String data = raw.replace("\n", "").replace("\r", "");
		System.out.println(data);
		byte[] messageBytes = data.getBytes();
		//byte[] messageBytes = "ABC".getBytes();
		signature.update(messageBytes);

		String receivedSignature="TvYOvpx09nHCsbArNdSp74KwKQqHOJGSz2y6LcqGMVSusMX7ysBh2MuMhpG9gy0ezBa5NOA4yLrzR/9oI3u/KaAK456dCfor9QGexop/WBHPt3zur7evCBmW0v+yMmdGNcDWL4CDcUlKbsVjd7zCjhoi2tfTEN1yx85H61MzmI9/uSVZUqzv48BUMeOtPeNrx2VBlu6NjDWFJL5HY3G578m1+Hpk6Ej1c2vXWjgUv7yO6CoPSVMJR4XzswvUlsY40HciS2erRb8Chfsj3C7UkAcGN/BiAfG2NYsYdGGjDvHdxrpBrv/VVLXxYesFmc6gDe38Ka9a8jL516Gf51bhnw==";
		byte[] decodedBytes = java.util.Base64.getDecoder().decode(receivedSignature);		
		//System.out.println(new String(decodedBytes));
		boolean isCorrect = signature.verify(decodedBytes);
		System.out.println(isCorrect);
		System.out.println("PKI .... Done!");
	}

	public static String toHexString(byte[] array) {
    		return DatatypeConverter.printHexBinary(array);
	}

	public static byte[] toByteArray(String s) {
    		return DatatypeConverter.parseHexBinary(s);
	}

	public static RSAPublicKey readPublicKey(File file) throws Exception {
    		KeyFactory factory = KeyFactory.getInstance("RSA");

    		try (FileReader keyReader = new FileReader(file);
      			PEMParser pemReader = new PEMParser(keyReader)) {

        		PemObject pemObject = pemReader.readPemObject();
        		byte[] content = pemObject.getContent();
        		X509EncodedKeySpec pubKeySpec = new X509EncodedKeySpec(content);
        		return (RSAPublicKey) factory.generatePublic(pubKeySpec);
    		}
	}
}
