# emailIdx
Synchronizes emails from IMAP to Elasticsearch

## Dependencies
First of all you need to install some dependencies which are:
```bash
$ # The obvious ones:
$ sudo apt-get install python python-pip
$ # If you want to:
$ sudo apt-get install python-virtualenv
$ # The less obvious ones:
$ sudo apt-get install  swig libssl-dev python-dev gnupg libxml2-dev libxslt1-dev
```

Of course you also need to run an IMAP server and an Elasticsearch server on which you'll operate.
But these don't need to run on the same machine as `emailIdx`

## Installing
Before you perform the actual install you may would like to set up a virtuale environment and activate it, e.g.:
```bash
$ virtualenv EIDX_ENV
$ . EIDX_ENV/bin/activate
```
Now let's do the install. It's as easy as issuing:
```bash
$ python setup.py install
```
All Python dependencies will be installed automatically. If you're interested in the list of dependency packages though, take a look at https://github.com/p-ho/emailIdx/blob/master/setup.py#L71

## Adjust settings
Now you've to create a settings file containing all necessary preferences to run the application.
For that purpose you could use https://github.com/p-ho/emailIdx/blob/master/sample_settings.json as a template.

## Running
Before running you must declare the location of the settings file by an environment variable as follows:
```bash
$ export EIDX_SETTINGS_FILE=/the/path/to/your/.../settings.json
```
Finally you can start the syncing process by issuing:
```bash
$ emailidx
```

## Outlook
After successful execution the (serialized and analyzed) cotent of the e-mails will be stored in the Elasticsearch database.
Now you can use [emailIdxQuery](https://github.com/p-ho/emailIdxQuery) as a frontend to search in that data.

