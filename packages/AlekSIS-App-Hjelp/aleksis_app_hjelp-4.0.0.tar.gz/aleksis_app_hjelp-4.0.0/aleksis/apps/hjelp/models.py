from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from aleksis.core.data_checks import field_validation_data_check_factory
from aleksis.core.mixins import ExtensibleModel, GlobalPermissionModel
from aleksis.core.util.model_helpers import ICONS


class HjelpGlobalPermissions(GlobalPermissionModel):  # noqa: DJ10,DJ11,DJ08
    class Meta:
        managed = False
        permissions = (
            ("view_faq", _("Can view FAQ")),
            ("ask_faq", _("Can ask FAQ question")),
            ("report_issue", _("Can report issues")),
            ("send_feedback", _("Can send feedback")),
        )


class FAQSection(ExtensibleModel):
    data_checks = [field_validation_data_check_factory("hjelp", "FAQSection", "icon")]

    name = models.CharField(max_length=255, verbose_name=_("Name"), unique=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        default="question_answer",
        choices=ICONS,
        verbose_name=_("Icon"),
    )

    show = models.BooleanField(verbose_name=_("Show"), default=False)

    position = models.PositiveIntegerField(verbose_name=_("Order"), default=1, blank=True)

    class Meta:
        verbose_name = _("FAQ section")
        verbose_name_plural = _("FAQ sections")
        ordering = ["position"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("order_faq")

    @property
    def visible_questions(self):
        return self.questions.filter(show=True)


class FAQQuestion(ExtensibleModel):
    data_checks = [field_validation_data_check_factory("hjelp", "FAQQuestion", "icon")]

    question_text = models.TextField(verbose_name=_("Question"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="question_answer",
        choices=ICONS,
        verbose_name=_("Icon"),
    )

    show = models.BooleanField(verbose_name=_("Show"), default=False)

    answer_text = RichTextField(verbose_name=_("Answer"))

    section = models.ForeignKey(
        FAQSection,
        on_delete=models.CASCADE,
        blank=True,
        related_name="questions",
        verbose_name=_("FAQ Section"),
    )

    class Meta:
        verbose_name = _("FAQ question")
        verbose_name_plural = _("FAQ questions")

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return reverse("order_faq")


class IssueCategory(ExtensibleModel):
    data_checks = [field_validation_data_check_factory("hjelp", "IssueCategory", "icon")]

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="bug_report",
        choices=ICONS,
        verbose_name=_("Icon"),
    )
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Parent category"),
    )
    free_text = models.BooleanField(verbose_name=_("Free text input allowed"), default=False)
    placeholder = models.CharField(max_length=255, verbose_name=_("Placeholder"), blank=True)

    class Meta:
        verbose_name = _("Issue category")
        verbose_name_plural = _("Issue categories")

        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(parent=None),
                name="unique_category_name_without_parent",
            ),
            models.UniqueConstraint(
                fields=["name", "parent"],
                name="unique_category_name_with_parent",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.free_text and self.children.exists():
            IssueCategory.objects.filter(parent=self).delete()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("admin:hjelp_issuecategory_change", args=[self.id])
