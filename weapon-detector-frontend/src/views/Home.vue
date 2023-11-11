<template>
  <v-container class=" mb-6">
    <v-row
        align="start"
        no-gutters
        style="height: 400px;"
        v-for="n in 3"
      >
      <v-col
          v-for="n in 3"
          :key="n"
          class="mr-10"
        >
        <v-card
          class="mx-auto"
          max-width="400"
        >
          <v-img
            class="align-end text-white"
            height="200"
            src=""
            cover
          >
            <v-card-title>ОрешкаТаманская</v-card-title>
          </v-img>

          <v-card-subtitle class="pt-4">
            2023-11-07 10:35
          </v-card-subtitle>

          <v-card-text>
            <div>Инциденты: 10</div>
          </v-card-text>

          <v-card-actions>
            <v-btn color="primary">
              Изменить
            </v-btn>
            <a href="/incidents">
            <v-btn color="primary">
              Инциденты
            </v-btn>
          </a>
          </v-card-actions>
        </v-card>
        </v-col>
    </v-row>
    <!-- <v-responsive class="align-center text-center fill-height">
      
    </v-responsive> -->
  </v-container>
</template>

<script setup>
</script>
