<template>
    <v-card
            class="mx-auto"
            max-width="400"
          >
            <v-img
              class="align-end text-white"
              height="200"
              :src="this.host + 'preview/' + this.id"
              cover
            >
              <v-card-title>{{this.name}}</v-card-title>
            </v-img>
  
            <v-card-subtitle class="pt-4">
              {{this.created_at}}
            </v-card-subtitle>
  
            <v-card-text>
                <v-progress-linear
                    model-value="100"
                    bg-color="blue-grey"
                    color="primary"
                    :indeterminate="!this.isActive"
                    ></v-progress-linear>
            </v-card-text>
  
            <v-card-actions>
              <v-btn color="primary" :href="'results/' + this.id" :disabled="!this.isActive">
                Результаты
              </v-btn>
            </v-card-actions>
          </v-card>
        </template>

<script>
import axios from "axios"


export default {
    name: 'ReportCard',
    data () {
        return {
            host: "http://195.239.123.50:9090/",
            isActive: false,
            created_at: null
        }
    },
    props: {
        id: Number,
        name: String
    },
    methods: {
      getOrder() {
                axios.get(this.host + 'order/' + this.id)
                .then((resp) => {
                this.created_at = resp.data.created_at
                if (resp.data.finished_at == null) {
                  this.isActive = false
                }
                else {
                  this.isActive = true
                }
            }).catch(function (er) {
                console.log(er);
            });
            }
    },
    mounted() {
      this.getOrder()
      setInterval(() => {
            this.getOrder()
        }, 5000);
    }
}
    
</script>