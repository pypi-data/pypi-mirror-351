from django.db.models.signals import m2m_changed, post_save

from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.matrix"
    verbose_name = "AlekSIS — Matrix (Integration with Matrix/Element)"
    dist_name = "AlekSIS-App-Matrix"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official//AlekSIS-App-Matrix",
    }
    licence = "EUPL-1.2+"
    copyright_info = (([2021, 2022], "Jonathan Weth", "dev@jonathanweth.de"),)

    def ready(self):
        from aleksis.core.models import Group

        from .models import MatrixProfile, MatrixRoom
        from .signals import m2m_changed_matrix_signal, post_save_matrix_signal

        post_save.connect(post_save_matrix_signal, sender=Group)
        post_save.connect(post_save_matrix_signal, sender=MatrixProfile)
        post_save.connect(post_save_matrix_signal, sender=MatrixRoom)

        m2m_changed.connect(m2m_changed_matrix_signal, sender=Group.members.through)
        m2m_changed.connect(m2m_changed_matrix_signal, sender=Group.owners.through)
