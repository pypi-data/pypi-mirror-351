export default {
  meta: {
    inMenu: true,
    titleKey: "matrix.menu_title",
    icon: "mdi-forum-outline",
    iconActive: "mdi-forum",
    permission: "matrix.view_matrixrooms_rule",
  },
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
  },
  children: [
    {
      path: "rooms/",
      component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),
      name: "matrix.groupsAndRooms",
      meta: {
        inMenu: true,
        titleKey: "matrix.rooms.menu_title",
        icon: "mdi-account-group-outline",
        iconActive: "mdi-account-group",
        permission: "matrix.view_matrixrooms_rule",
      },
      props: {
        byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
      },
    },
  ],
};
