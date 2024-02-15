
from .models import Core
from .test_cpe import Service_Validation


def get_services_affecteds(id):
    try:
        # get core table
        core_table = Core.objects.get(id=id)
        # get affected services from database
        services_affecteds = core_table.affected_services
        # validate services affecteds
        result = Service_Validation(services_affecteds)
        return result
    except Core.DoesNotExist:
        print(f"Core ID {id} Not Found ")
        return None

