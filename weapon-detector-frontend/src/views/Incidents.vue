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
          <div class="ma-4">
            <a href="https://cdn.vuetifyjs.com/images/parallax/material.jpg">
            <v-img
                class="bg-grey-lighten-4"
                width="300"
                :aspect-ratio="1"
                src="https://cdn.vuetifyjs.com/images/parallax/material.jpg"
            >
            </v-img>
          </a>
            </div>
          </v-col>
      </v-row>
      <!-- <v-responsive class="align-center text-center fill-height">
        
      </v-responsive> -->
    </v-container>
  </template>
  
  <script>

  </script>