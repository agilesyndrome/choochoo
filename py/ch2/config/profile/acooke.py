
from ..config import Config, WALK, SWIM, RUN, BIKE
from ..database import add_diary_topic, add_child_diary_topic, add_diary_topic_field, add_enum_constant, \
    add_constant
from ..power import add_simple_power_estimate
from ...commands.args import DEFAULT, base_system_path, PERMANENT
from ...diary.model import TYPE, EDIT
from ...lib import to_time, time_to_local_date
from ...msil2a.download import MSIL2A_DIR_CNAME
from ...names import Sports
from ...pipeline.read.activity import ActivityReader
from ...sql import StatisticJournalType, StatisticName, DiaryTopic, DiaryTopicJournal
from ...sql.tables.statistic import STATISTIC_JOURNAL_CLASSES
from ...sql.utils import add


def acooke(sys, s, base, no_diary=False):
    '''
## acooke

This extends the default configuration with:

* Diary entries that I need
* Additional activity groups selected on the kit used
* Power estimates

Unlikely to be useful to others, but works as an example of how you can extend the code yourself.
    '''
    ACooke(sys, base, no_diary=no_diary).load(s)


ROAD = 'Road'
MTB = 'MTB'


class ACooke(Config):

    def _load_diary_topics(self, s, c):
        super()._load_diary_topics(s, c)

        # add more diary entries specific to my needs

        injuries = add_diary_topic(s, 'Injuries', c)

        ms = add_child_diary_topic(s, injuries, 'Multiple Sclerosis', c)
        add_diary_topic_field(s, ms, 'MS Notes', c, StatisticJournalType.TEXT, model={TYPE: EDIT})
        add_child_diary_topic(s, ms, 'Betaferon', c,
                              schedule='2018-08-08/2d[1]')  # reminder to take meds on alternate days

        leg = add_child_diary_topic(s, injuries, 'Broken Femur LHS', c,
                                    schedule='d2018-03-11-2020-03-01')
        add_diary_topic_field(s, leg, 'Leg Notes', c, StatisticJournalType.TEXT, model={TYPE: EDIT})
        add_child_diary_topic(s, leg, 'Learn to manage tendon pain', c)  # aims added as child topics
        add_child_diary_topic(s, leg, 'Maintain fitness', c)
        add_child_diary_topic(s, leg, 'Visit UK', c, schedule='-2018-08-11')

    def _load_specific_activity_groups(self, s):
        super()._load_specific_activity_groups(s)

        # additional activity groups for different cycling activities

        self._load_activity_group(s, ROAD, 'Road cycling activities')
        self._load_activity_group(s, MTB, 'MTB cycling activities')

    def _sport_to_activity(self):

        # map the additional groups above based on kit use
        # (cotic and bowman are kit items added via kit commands)

        return {Sports.SPORT_CYCLING: {
                    ActivityReader.KIT: {
                        'cotic': MTB,
                        'bowman': ROAD,
                    },
                    DEFAULT: BIKE,
                },
                Sports.SPORT_RUNNING: RUN,
                Sports.SPORT_SWIMMING: SWIM,
                Sports.SPORT_WALKING: WALK}

    def _load_power_statistics(self, s, c):
        # add power estimates for the two bikes
        # (note that this comes after standard stats, but before summary, achievements, etc).
        for activity_group in (MTB, ROAD):
            activity_group = self._activity_groups[activity_group]
            add_simple_power_estimate(s, c, activity_group, 0.42, 0.0055, 12, 65)

    def _load_constants(self, s):
        super()._load_constants(s)
        add_constant(s, MSIL2A_DIR_CNAME, base_system_path(self._base, version=PERMANENT, subdir='msil2a', create=False),
                     description='''
Directory containing Sentinel 2A imaging data (see https://scihub.copernicus.eu/dhus/#/home)

This can be used to generate background images for plots.
I used the data in an experiment to generate 3D plots, but it wasn't very successful.
''',
                     single=True, statistic_journal_type=StatisticJournalType.TEXT)

    def _post(self, s):
        super()._post(s)
        # set a default weight for early power calculations
        weight = s.query(StatisticName).filter(StatisticName.name == 'Weight', StatisticName.owner == DiaryTopic).one()
        diary = add(s, DiaryTopicJournal(date=time_to_local_date(to_time(0.0))))
        add(s, STATISTIC_JOURNAL_CLASSES[weight.statistic_journal_type](
            value=65.0, time=0.0, statistic_name=weight, source=diary))
