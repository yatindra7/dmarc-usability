#include <resolv.h>
#include <string.h>
#include <stdio.h>

struct bounds{int start,end;};

struct bounds findSPF(char *response, int responseLength) {
    struct bounds ret;
    ret.start=-1;
    ret.end=-1;
    char spf[]="v=spf1";
    char all[]="all";
    int i, j, k;
    // Iterate through the response
    for (i = 0; i <= responseLength - sizeof(spf); i++)
    {
	// Check if the current position matches the start
	int match = 1;
        for (j = 0; j < sizeof(spf)-1; j++) {
            if (response[i + j] != spf[j]) {
                match = 0;
                break;
            }
        }
        // If found, store the index
        if (match)
        {
	    ret.start=i;
	    for (j=ret.start; j < responseLength; j++)
    	    {
                // Check for DLE
		if (j==responseLength||response[j]=='\x10'||response[j]=='\x1c'||response[j]=='\x01'||response[j]=='\x18')
		{
		    ret.end=j;
		    return ret;
		}
	    }
	    ret.end=j;
	    return ret;
    	}
    }
    // If not found, return -1
    return ret;
}

int main() {
    // Open the file for reading
    FILE *file = fopen("domains10k.txt", "r");

    // Check if the file was opened successfully
    if (file == NULL) {
        perror("Error opening file");
        return 1; // Exit the program with an error code
    }

    // Buffer to read each line from the file
    char hostname[64];
    while (fscanf(file, "%255[^\n]%*c", hostname) == 1)
    //while (fgets(hostname, sizeof(hostname), file) != NULL)
    {
	printf("%s\t",hostname);
    	struct __res_state res;

    	// Initialize resolver state
    	if (res_ninit(&res) < 0) {
        	perror("res_ninit");
        	return 1;
    	}

    	// Perform DNS TXT query for SPF record
    	unsigned char answer[NS_PACKETSZ*5];
    	int responseLength = res_nquery(&res, hostname, C_IN, T_TXT, answer, sizeof(answer));

    	if (responseLength < 0) {
        	printf("%s",hostname);
		perror("res_nquery");
        	res_nclose(&res);
        	continue;
    	}
    	else
    	{
		int i,j,k;
        	//for(i=0;i<responseLength; i++)
            		//printf("%c", (char)(answer[i]));
		//printf("\n %d \n", NS_PACKETSZ);

		struct bounds find = findSPF(answer,responseLength);
		//printf("%d %d",find.start,find.end);
		for(k=find.start;k<find.end;k++)
	    		printf("%c", (char)(answer[k]));
		printf("\n");
    	}

    	// Close resolver state
    	res_nclose(&res);
    }
    return 0;
}
