from Products.CMFCore.utils import getToolByName
import gdata.auth
from collective.googleanalytics import error
from collective.googleanalytics.interfaces.utility import \
    IAnalyticsReportsAssignment, IAnalyticsTracking, IAnalyticsSettings

from plone.directives import form

from z3c.form import field
from z3c.form import button

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalyticsControlPanelForm(form.Form):

    """
    Google Analytics Control Panel Form
    """
    fields = field.Fields(IAnalyticsReportsAssignment, IAnalyticsTracking, IAnalyticsSettings)
    template = ViewPageTemplateFile('controlpanel.pt')
    ignoreContext = True
    label = u"Google Analytics"
    form_name = u"Google Analytics Settings"

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here'
        print "Run _on_save ?"
        # import pdb; pdb.set_trace()

        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.status = "Thank you very much!"

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        # import pdb; pdb.set_trace()

    def authorized(self):
        """
        Returns True if we have an auth token, or false otherwise.
        """
        if self.context.auth_token:
            return True
        return False

    def auth_url(self):
        """
        Returns the URL used to retrieve a Google AuthSub token.
        """

        next = '%s/analytics-auth' % self.context.portal_url()
        scope = 'https://www.google.com/analytics/feeds/'

        return gdata.auth.GenerateAuthSubUrl(next, scope, secure=False, session=True)

    def account_name(self):
        """
        Returns the account name for the currently authorized account.
        """

        analytics_tool = getToolByName(self.context, 'portal_analytics')

        try:
            res = analytics_tool.getAccountsFeed('accounts')
        except error.BadAuthenticationError:
            return None
        except error.RequestTimedOutError:
            return None
        return res.title.text.split(' ')[-1]

    def _on_save(self, data={}):
        """
        Checks to make sure that tracking code is not duplicated in the site
        configlet.
        """

        tracking_web_property = data.get('tracking_web_property', None)
        properties_tool = getToolByName(self.context, "portal_properties")
        snippet = properties_tool.site_properties.webstats_js
        snippet_analytics = '_gat' in snippet or '_gaq' in snippet
        if tracking_web_property and snippet_analytics:
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage((u'You have enabled the tracking \
            feature of this product, but it looks like you still have tracking \
            code in the Site control panel. Please remove any Google Analytics \
            tracking code from the Site control panel to avoid conflicts.'), 'warning')
