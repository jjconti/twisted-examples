from twisted.web.client import getPage

from twisted.internet import reactor

def lowerCaseContents(contents):
    '''
    This is a 'callback' function, added to the Deferred and called by
    it when the promised data is available. It converts all the data to
    lower case
    '''

    return contents.upper()

def printContents(contents):
    '''
    This is the 'callback' function, added to the Deferred and called by
    it when the promised data is available
    '''

    print "The Deferred has called printContents with the following contents:"
    print contents

    # Stop the Twisted event handling system -- this is usually handled
    # in higher level ways
    reactor.stop()

def errorHandler(error):
    '''
    This is an 'errback' function, added to the Deferred which will call
    it in the event of an error
    '''

    # this isn't a very effective handling of the error, we just print it out:
    print "An error has occurred: <%s>" % str(error)
    # and then we stop the entire process:
    reactor.stop()

# call getPage, which returns immediately with a Deferred, promising to
# pass the page contents onto our callbacks when the contents are available
deferred = getPage('http://twistedmatrix.com/noexiste')

print deferred

# add a callback to the deferred -- request that it run printContents when
# the page content has been downloaded
# A very common use of Deferreds is to attach two callbacks. 
# The result of the first callback is passed to the second callback:
deferred.addCallback(lowerCaseContents)
deferred.addCallback(printContents)

# add the errback to the Deferred to handle any errors
deferred.addErrback(errorHandler)

# Begin the Twisted event handling system to manage the process -- again this
# isn't the usual way to do this
reactor.run()

