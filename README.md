# SNKRSBot: A multi-task bot for buying sneakers from the Nike Netherlands. 

Before running, make sure to fill the NikeRes\ShippingDetails.csv file carefully.

*******************************************************************************************

Author: Ali Toori, Full-Stack Python Developer, Bot-Builder.

Founder: https://boteaz.com

YouTube: https://youtube.com/@AliToori

Telegram: https://t.me/@AliToori
*******************************************************************************************

# Usage
Install the required packages by running the following command.
    
    pip install -r requirements.txt

Run the following command in terminal opened at the main folder.
    
    python NikeBot.py

Here is a list and description of the different items to fill:

<b>AccountNo</b>
* AccountNo for each account. Important

<b>Email</b>
* Email for your Nike login

<b>Password</b>
* Password for your Nike login

<b>GmailID</b>
* You Gmail ID for Google login.

<b>GmailPassword</b>
* You Gmail Password for Google login.

<b>ProductURL</b>
* URL for desired shoe: If you don't know the URL, just put Nike home url.
You can add URL at run time to the URL.txt file and hit save.

<b>Browser</b>
* Browser type: Default is chrome. If you want to use FireFox, please download geckodedriver and put into the bin folder. 

<b>Proxy</b>
* Proxy for each account: Default is set to No. If you want to use proxy, please follow the format '192.162.10.5:8080'. 

<b>ShoesSize</b>
* Size of shoes to be selected on the item page. 

<b>Shoes Color</b>
* Shoes color: Default is White. You can put any color name. The bot will select that color for you.

<b>LoginTime</b>
* If given, the bot will pause until a specific time before it logs in (can be any datetime format)

<b>ReleaseTime</b>
* If given, the bot will pause until a specific time before it purchase the sneaker (can be any datetime format)

<b>ScreenshotPath</b>
* If given, the bot will take a screenshot of the page after purchasing and save it at the given file path.

<b>Headless</b>
* Defualt is "Yes". Only for first time loging in to Google and Nike accounts.
This will run the driver in headless mode, which will make the bot faster.

<b>ChangePayment</b>
* Default is No. If you already have your payment options pre-saved on your Nike account, DO NOT use this. If for some reason you don't have it pre-saved (even though it will cost the bot more time) the bot will select the first payment option it finds.

<b>Purchase</b>
* Default is Yes. If this argument is given as No, the bot WILL attempt on item to add-to-cart only.

<b>FirstName</b>
* First Name for new shipping address.

<b>LastName</b>
* Last Name for new shipping address.

<b>Address</b>
* Comlete address to be used for shipping.

<b>Phone</b>
* Phone number for new shipping address.

<b>EmailAddress</b>
* Email address for new shipping address.

<b>CardNumber</b>
* Credit card number for placing order.

<b>CardExpiry</b>
* Credit card expiry for placing order. Example: 12/25

<b>CVV</b>
* Credit card CVV for placing order.