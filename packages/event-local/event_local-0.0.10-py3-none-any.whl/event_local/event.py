# TODO Can we use event-local package instead of this file
from python_sdk_remote.our_object import OurObject

ENTITY_NAME = "Event"


class Event(OurObject):
    def __init__(self, **kwargs):
        event_fields = {
            "event_id",
            "number",
            "identifier",
            "name",
            "description",
            "type",
            "sub_type",
            "genre",
            "sub_genre",
            "segement",
            "visibility_id",
            "start_timestamp",
            "end_timestamp",
            "access_start_timestamp",
            "created_timestamp",
            "updated_timestamp",
            "location_id",
            "location_id_temp",
            "organizers_profile_id",
            "parent_event_id",
            "facebook_event_url",
            "meetup_event_url",
            "registration_url",
            "website_url",
            "is_beakfast",
            "is_lunch",
            "is_dinner",
            "is_family",
            "is_event_approved",
            "is_event_has_promoters",
            "is_paid",
            "is_can_be_paid_at_the_entrance_in_cash",
            "is_require_end_user_registration",
            "is_require_end_user_arrival_confirmation",
            "is_require_organizer_registration_confirmation",
            "is_show_end_timestamp",
            "is_test_data",
            "is_waitinglist",
            "created_effective_profile_id",
            "created_effective_user_id",
            "created_real_user_id",
            "created_user_id",
            "updated_effective_profile_id",
            "updated_effective_user_id",
            "updated_real_user_id",
            "updated_user_id",
        }

        # for field, value in kwargs.items():
        #     if field in event_fields:
        #         setattr(self, field, value)

    def __init__(self, entity_name=ENTITY_NAME, **kwargs):
        super().__init__(entity_name, **kwargs)

    # Mandatory pure virtual method from OurObject
    def get_name(self):
        print(f"{ENTITY_NAME} get_name() self.fields.display_as={self.fields.display_as}")
        return self.fields.display_as

    # def get_name(self):
    #     return self.name

    # def __str__(self):
    #     return "event: " + str(self.__dict__)

    # def __repr__(self):
    #     return "event: " + str(self.__dict__)

    # def to_dict(self):
    #     return self.__dict__
