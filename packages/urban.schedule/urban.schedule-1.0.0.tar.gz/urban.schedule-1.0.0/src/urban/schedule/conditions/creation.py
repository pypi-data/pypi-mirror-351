# -*- coding: utf-8 -*-
from Products.urban.interfaces import ICODT_BaseBuildLicence
from Products.urban.interfaces import IIntentionToSubmitAmendedPlans
from Products.urban.interfaces import IDepositEvent
from datetime import datetime
from imio.schedule.content.condition import CreationCondition


class IsCODT2024(CreationCondition):
    """Validate that the current licence is impacted by the new CODT reform"""

    def evaluate(self):
        licence = self.task_container
        return licence.is_CODT2024()


class IsNotCODT2024(CreationCondition):
    """Validate that the current licence is not impacted by the new CODT reform"""

    def evaluate(self):
        licence = self.task_container
        return licence.is_CODT2024() is not True


class HasAmendedPlans(CreationCondition):
    """"""

    def evaluate(self):
        licence = self.task_container
        event = licence.getLastEvent(IIntentionToSubmitAmendedPlans)
        return event is not None


class IsPloneMeetingCollegeDone(CreationCondition):
    def evaluate(self):
        licence = self.task_container
        if ICODT_BaseBuildLicence.providedBy(licence):
            return True if licence.get_last_college_date() else False



class IsPloneMeetingCouncilDone(CreationCondition):
    def evaluate(self):
        licence = self.task_container
        if ICODT_BaseBuildLicence.providedBy(licence):
            return True if licence.get_last_council_date() else False


class DepositDateIsPast20Days(CreationCondition):
    """The deposit date is past by 20 days"""

    def evaluate(self):
        licence = self.task_container

        deposit_event = licence.getLastDeposit()
        if deposit_event:
            date1 = deposit_event.eventDate.asdatetime()
            date2 = datetime.now(date1.tzinfo)
            return (date2.date() - date1.date()).days > 20
        return False


class DepositDateIsUnder20Days(DepositDateIsPast20Days):
    """The deposit date is under 20 days"""

    def evaluate(self):
        return not super(DepositDateIsUnder20Days, self).evaluate()


class DepositNumberMatch(CreationCondition):
    """Verify if for the given task, the number of task is not above
    the number of deposit"""

    def evaluate(self):
        licence = self.task_container
        deposit_events = licence.getAllEvents(eventInterface=IDepositEvent)
        deposit_events.extend(licence.getAllEvents(eventInterface=IIntentionToSubmitAmendedPlans))
        tasks = self.task_config.get_task_instances(self.task_container)
        return len(tasks) < len(deposit_events)