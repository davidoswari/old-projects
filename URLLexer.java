import java.util.regex.*;
import java.io.*;
import java.util.*;
import java.net.*;
//David Oswari G01013002
public class URLLexer
{
	// These are the 7 tokens in our simplified URL definition
   public static final int PROTOCOL = 0;
   public static final int NUMERICAL_ADDRESS = 1;
   public static final int NON_NUMERICAL_ADDRESS = 2;
   public static final int PORT = 3;
   public static final int FILE = 4;
   public static final int FRAGMENT = 5;
   public static final int QUERY = 6;
	
	// Here you place regular expressions, one per token.  Each is a string.
   public static final String[] REGULAR_EXPRESSION = 
   	new String[]
   		{
   		"\\G[a-zA-Z]*://?",  // protocol
   		"\\G(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0[0-9][0-9]|[1-9][0-9]|[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0[0-9][0-9]|[1-9][0-9]|[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0[0-9][0-9]|[1-9][0-9]|[0-9])\\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|0[0-9][0-9]|[1-9][0-9]|[0-9])", // numerical address
   		"\\G[0-9A-Za-z-.]*[0-9A-Za-z-]", // non-numerical address
   		"\\G:[0-9]*", // port
   		"\\G/[^#?]*", // file
   		"\\G#.*", // fragment
   		"\\G\\?.*", // query
   		};

	// This is an array of names for each of the tokens, which might be convenient for you to
	// use to print out stuff.
   public static final String[] NAME = new String[] { "protocol", "numerical address", "non-numerical address",
   												   "port", "file", "fragment", "query" };
                                          
   private int position;
   private int matchIndex;
   private String url;
   String[] tokens = new String[7];
   static Scanner input = new Scanner(System.in);
   Matcher matcher;
   
	/** Creates a Blank URLLexer set up to do pattern-matching on the given regular expressions. */
   public URLLexer()
   {
   	// IMPLEMENT ME (ABOUT 5 LINES)
      String url = "";
      position=0;
      matchIndex=0;
      for(int i=0;i<7;i++)
         tokens[i] = null;
   }
	
	/** Resets the URLLexer to a new string as input. */
   public void reset(String input)
   {
   	// IMPLEMENT ME (ABOUT 3 LINES)
      position=0;
      matchIndex=0;
      url = input;
      tokens = new String[7];
   }
	//return what kind of token
   public int getMatchingIndex()
   {
      return matchIndex;
   }
	//return current position of tokenizer	
   public int getPosition()
   { 
      return position;
   }
	
   public String nextToken()
   {
   	// IMPLEMENT ME (ABOUT 10 LINES)
      for(int i=0;i<7;i++)
      {
         Pattern pattern = Pattern.compile(REGULAR_EXPRESSION[i],Pattern.DOTALL);
         matcher = pattern.matcher(url);
         if(matcher.find(getPosition())&& tokens[i]==null)
         {
            matchIndex = i;
            tokens[getMatchingIndex()] = matcher.group();
            position=matcher.end();
            return matcher.group();
         }
      }
      return null;
   }
   public static void main(String[] args) throws IOException
   {
   	// IMPLEMENT ME.
   	//
   	// You will repeatedly request a URL by printing "URL: ".  Once the user has provided
   	// a URL, you will trim it of whitespace, then tokenize it.  As you tokenize it you 
   	// will print out the tokens one
   	// by one, including their token types.  If you find a duplicate token type, you will
   	// FAIL.  You will also FAIL if the tokenizer cannot recognize any further tokens but
   	// you still have characters left to tokenize.  If you manage to finish tokenizing
   	// a URL, you will pass the tokens to the fetch(...) function provided below.  Whenever
   	// a failure occurs, you will indicate it, then loop again to request another URL.
      
      //create object
      URLLexer ul = new URLLexer();
      //infinite loop
      while(true)
      {
         System.out.println("Enter a URL or 'q' to exit");
      //get user input with no spaces
         System.out.print("URL: ");
         ul.reset(input.nextLine().replaceAll(" ",""));
         //exit loop
         if(ul.url.equals("q"))
            break;
         
         //tokenize the url and store tokens in array
         for(int i=0;i<7;i++)
            ul.nextToken();
         
         //recreate url with tokens for comparison
         String urlToken="";
         for(int j=0;j<7;j++)
         {
            if(ul.tokens[j]!=null)
               urlToken = urlToken + ul.tokens[j];
            System.out.println(NAME[j] + " = " + ul.tokens[j]);
         }
      
          //fail case: if reconstructed url does not match original length
         if(ul.url.length()!=urlToken.length())
            System.out.println("FAIL.");
         else
            fetch(ul.tokens[0],ul.tokens[1],ul.tokens[2],ul.tokens[3],ul.tokens[4],ul.tokens[6],ul.tokens[5]);
            
         //for spacing
         System.out.println("");
      }
      
   }

	// perhaps this function might come in use.
	// It takes various tokenized values, checks them for validity, then fetches the data
	// from a URL formed by them and prints it to the screen.
   public static void fetch(String protocol, String numericalAddress, String nonNumericalAddress,
   						String port, String file, String query, String fragment)
   {
      String address = numericalAddress;
      int iport = 80;
   
   	// verify the URL
      if (protocol == null || !protocol.equals("http://"))
      {
         System.out.println("ERROR. I don't know how to use protocol " + protocol);
      }
      else if (query != null)
      {
         System.out.println("ERROR. I'm not smart enough to issue queries, like " + query); 
      }
      else if (numericalAddress == null && nonNumericalAddress == null)
      {
         System.out.println("ERROR. No address was provided.");
      }
      else if (numericalAddress != null && nonNumericalAddress != null)
      {
         System.out.println("ERROR. Both types of addresses were provided.");
      }
      else
      {
         if (address == null)
         {
            address = nonNumericalAddress;
         }
         if (fragment != null)
         {
            System.out.println("NOTE. Fragment provided: I will not use it.");
         }
         if (port != null)
         {
            iport = Integer.parseInt(port.substring(1));  // strip off the ":"
         }
         else  
         {
            System.out.println("NOTE. No port provided, defaulting to port 80.");
         }
         if (file == null)
         {
            System.out.println("NOTE. No file was provided.  Assuming it's just /");
            file = "/";
         }
      	
         System.out.println("Downloading ADDRESS: " + address + " PORT: " + iport + " FILE: " + file);
         System.out.println("\n=======================================");
      
         java.io.InputStream stream = null;
         try
         {				
            java.net.URL url = new java.net.URL("http", address, iport, file);
            java.net.URLConnection connection = url.openConnection();
            connection.connect();
            stream = connection.getInputStream();
            final int BUFLEN = 1024;
            byte[] buffer = new byte[BUFLEN];
            while(true)
            {
               int len = stream.read(buffer, 0, BUFLEN);
               if (len <= 0) 
                  break;
               System.out.write(buffer, 0, len);
            }
         }
         catch (java.io.IOException e)
         {
            System.out.println("Error fetching data.");
         }
         try
         {
            if (stream != null) stream.close();
         }
         catch (java.io.IOException e) { }
         System.out.println("\n=======================================");
      }
   }
}