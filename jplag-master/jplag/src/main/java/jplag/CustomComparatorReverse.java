package jplag;

import java.util.Comparator;

public class CustomComparatorReverse implements Comparator<String> {

    @Override
    public int compare(String str1, String str2) {
    	int num1 = 0, num2 = 0;
    	if (str1.substring(0, 1).equals("~") && str2.substring(0, 1).equals("~")){
    		num1 = Integer.parseInt(str1.substring(1, str1.indexOf(" ")));
        	num2 = Integer.parseInt(str2.substring(1, str2.indexOf(" ")));
    	} else if (str1.substring(0, 1).equals("~")){
    		return 1;
    	} else if (str2.substring(0, 1).equals("~")){
    		return -1;
    	} else {
    		num1 = Integer.parseInt(str1.substring(0, str1.indexOf(" ")));
        	num2 = Integer.parseInt(str2.substring(0, str2.indexOf(" ")));
    	}
        return num2 - num1;
    }
}