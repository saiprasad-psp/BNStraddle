# BNStraddle
Bank Nifty Straddle

It works for Fyers only.

You need userinfo.json file with contents
{
         "app_id": "<YourFyersAppID>",
         "app_secret": "<YourFyersAppSecretForAboveFyersID>",
         "fyers_id": "<YourFyersLoginID>",
         "password": "<YourPassword>",
         "pan_or_dob": "<YourPanNumberORDateOfBirthIn_dd-mm-yyyy_format>"
}
         
Folders are hardcoded please change as per your requirement.
         
autologin.py will authenticate user and create file access_token.txt
         
BNFStraddle.py will use the file access_token.txt and place orders.

To send messages to telegram -

         Create a bot in telegram and save the token in the file bot_token.txt
         Create a new channel and add the above created bot to the channel then save the chat ID in the file bot_chatID.txt.
