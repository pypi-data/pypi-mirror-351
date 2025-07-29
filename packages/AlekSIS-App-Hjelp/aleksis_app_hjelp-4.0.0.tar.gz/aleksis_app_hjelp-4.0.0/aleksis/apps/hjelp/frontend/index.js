export default {
  meta: {
    inMenu: true,
    titleKey: "hjelp.menu_title",
    icon: "mdi-help-circle-outline",
    iconActive: "mdi-help-circle",
    permission: "hjelp.show_menu_rule",
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "issues/report/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.reportIssue",
      meta: {
        inMenu: true,
        titleKey: "hjelp.issues.menu_title",
        icon: "mdi-bug-outline",
        iconActive: "mdi-bug",
        permission: "hjelp.report_issue_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "feedback/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.feedback",
      meta: {
        inMenu: true,
        titleKey: "hjelp.feedback.menu_title",
        icon: "mdi-message-text-outline",
        iconActive: "mdi-message-text",
        permission: "hjelp.send_feedback_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.faq",
      meta: {
        inMenu: true,
        titleKey: "hjelp.faq.menu_title_list",
        icon: "mdi-forum-outline",
        iconActive: "mdi-forum",
        permission: "hjelp.view_faq_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/ask/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.askFaq",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/order/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.orderFaq",
      meta: {
        inMenu: true,
        titleKey: "hjelp.faq.menu_title_manage",
        icon: "mdi-priority-low",
        iconActive: "mdi-priority-high",
        permission: "hjelp.change_faq_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/section/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.createFaqSection",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/section/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.deleteFaqSection",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/question/create/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.createFaqQuestion",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/question/:pk/update/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.updateFaqQuestion",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
    {
      path: "faq/question/:pk/delete/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "hjelp.deleteFaqQuestion",
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
