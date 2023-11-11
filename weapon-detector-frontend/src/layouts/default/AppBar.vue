<template>
  <v-app-bar color="primary">
    <v-icon icon="mdiRobot"></v-icon>
    <v-app-bar-title>

      DDA
    </v-app-bar-title>
  </v-app-bar>
  <v-navigation-drawer expand-on-hover rail theme="dark">
    <v-divider></v-divider>

    <v-list density="compact" nav>
      <!-- <v-list-item prepend-icon="mdi-video" title="Live-камеры" value="live" href="/"></v-list-item> -->
      <v-list-item prepend-icon="mdi-order-bool-descending-variant" title="Видео" value="reports"  href="/reports"></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
  //
</script>
