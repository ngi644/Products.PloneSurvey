import string
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import DisplayList

from Products.PloneSurvey.config import PROJECTNAME

from schemata import SubSurveySchema


class SubSurvey(ATCTOrderedFolder):
    """A sub page within a survey"""
    schema = SubSurveySchema
    _at_rename_after_creation = True
    portal_type = 'Sub Survey'
    security = ClassSecurityInfo()

    security.declarePublic('canSetDefaultPage')

    def canSetDefaultPage(self):
        """Doesn't make sense for surveys to allow alternate views"""
        return False

    security.declarePublic('canConstrainTypes')

    def canConstrainTypes(self):
        """Should not be able to add non survey types"""
        return False

    security.declareProtected(permissions.View, 'isMultipage')

    def isMultipage(self):
        """Return true if there is more than one page in the survey"""
        return True

    security.declareProtected(permissions.View, 'getSurveyId')

    def getSurveyId(self):
        """Return the userid for the survey"""
        request = self.REQUEST
        try:
            user_id = request.form['survey_user_id']
        except KeyError:
            pass
        else:
            portal_membership = getToolByName(self, 'portal_membership')
            if not portal_membership.isAnonymousUser():
                member_id = portal_membership.getAuthenticatedMember().getId()
                if member_id == user_id:
                    return user_id
            else:
                survey_cookie = self.aq_parent.getId()
                if self.aq_parent.getAllowAnonymous() and self.REQUEST.has_key(survey_cookie) and request.get(survey_cookie, "Anonymous") == user_id:
                    return user_id
            # XXX survey is probably being spoofed, need another field for
            # allow users without cookies, for now let them through
            return user_id
        survey_url = self.aq_parent.absolute_url()
        return self.REQUEST.RESPONSE.redirect(survey_url)

    security.declareProtected(permissions.ModifyPortalContent,
                              'getValidationQuestions')

    def getValidationQuestions(self):
        """Return the questions for the validation field"""
        portal_catalog = getToolByName(self, 'portal_catalog')
        questions = [('', 'None')]
        path = string.join(self.aq_parent.getPhysicalPath(), '/')
        results = portal_catalog.searchResults(
            portal_type=['Survey Select Question', ],
            path=path)
        for result in results:
            obj = result.getObject()
            title = '{}:{}'.format(obj.Title(), ','.join(obj.getQuestionOptions()))
            questions.append((obj.getId(), title))
        # vocab_list = DisplayList((questions))
        return DisplayList((questions))

    security.declareProtected(permissions.View, 'getBranchingCondition')

    def getBranchingCondition(self):
        """Return the title of the branching question"""
        branchings = ''
        required_question = self.getRequiredQuestion()
        branch_question = self[required_question]
        branchings = branch_question.Title() + ':' + self.getRequiredAnswer()
        return branchings

    security.declareProtected(permissions.View, 'getQuestions')

    def getQuestions(self):
        """Return the questions for this part of the survey"""
        questions = self.getFolderContents(
            contentFilter={'portal_type': [
                'Survey Date Question',
                'Survey Matrix',
                'Survey Select Question',
                'Survey Text Question',
                ]}, full_objects=True)
        return questions

    security.declareProtected(permissions.View, 'hasDateQuestion')

    def hasDateQuestion(self):
        """Return true if there is a date question in this part of the survey
        to import the js"""
        objects = self.getFolderContents(
            contentFilter={'portal_type': 'Survey Date Question'})
        if objects:
            return True
        return False

    security.declareProtected(permissions.View, 'checkCompleted')

    def checkCompleted(self):
        """Return true if this page is completed"""
        # XXX
        return True

    security.declareProtected(permissions.View, 'getNextPage')

    def getNextPage(self):
        """Return the next page of the survey"""
        previous_page = True
        parent = self.aq_parent
        pages = parent.getFolderContents(
            contentFilter={'portal_type': 'Sub Survey', }, full_objects=True)
        for page in pages:
            if previous_page:
                if page.getId() == self.getId():
                    previous_page = False
            elif page.displaySubSurvey():
                return page()
        return self.exitSurvey()

    security.declareProtected(permissions.View, 'hasMorePages')

    def hasMorePages(self):
        """Return True if survey has more pages to display"""
        previous_page = True
        parent = self.aq_parent
        pages = parent.getFolderContents(
            contentFilter={'portal_type': 'Sub Survey', }, full_objects=True)
        for page in pages:
            if previous_page:
                if page.getId() == self.getId():
                    previous_page = False
            elif page.displaySubSurvey():
                return True
        return False

    security.declareProtected(permissions.View, 'displaySubSurvey')

    def displaySubSurvey(self):
        """Determine whether this page should be displayed"""
        parent = self.aq_parent
        userid = parent.getSurveyId()
        required_question = self.getRequiredQuestion()
        required_questions = self.getRequiredQuestionsAnswers()
        if not required_question and not required_questions:
            return True
        # find the right question
        questions = []
        if required_question:
            questions.append({'question': required_question, 'answer': self.getRequiredAnswer()})
        if required_questions:
            questions = questions + list(required_questions)
        # TODO: this assumes that no questions exist with a duplicate id
        pages = parent.getFolderContents(
            contentFilter={'portal_type': 'Sub Survey', },
            full_objects=True)
        right_answer = False
        for qa in questions:
            if qa['question'] in parent.objectIds():
                question = parent[qa['question']]
                required_answers = qa['answer'].split('|')
                answer = question.getAnswerFor(userid)
                if hasattr(answer, 'lower'):
                    if answer in required_answers:
                        right_answer = True
                elif hasattr(answer, 'append'):  # it's a list
                    if len(set(required_answers) and set(answer)):
                        right_answer = True
            else:
                for page in pages:
                    if qa['question'] in page.objectIds():
                        question = page[qa['question']]
                        required_answers = qa['answer'].split('|')
                        answer = question.getAnswerFor(userid)
                        if hasattr(answer, 'lower'):
                            if answer in required_answers:
                                right_answer = True
                        elif hasattr(answer, 'append'):  # it's a list
                            if len(set(required_answers) and set(answer)):
                                right_answer = True
        # TODO: this assumes the question actually exists
        required_positive = self.getRequiredAnswerYesNo()
        # print(right_answer, required_positive)
        if required_positive and right_answer:
            return True
        elif not required_positive:
            return True
        return False


registerATCT(SubSurvey, PROJECTNAME)
