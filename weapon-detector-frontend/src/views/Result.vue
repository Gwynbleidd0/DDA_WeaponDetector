<template>
    <v-container class=" mb-6">
        <v-row>
            <v-col cols=8 class="ml-4">
                <v-img
                    class="bg-grey-lighten-4 "
                    :aspect-ratio="1.5"
                    :src="this.host + '/preview/' + this.id"
                    cover
                />
            </v-col>
            <v-col cols=3>
                <v-card-title class="text-h6 text-md-h5 text-lg-h4">{{this.name}}</v-card-title>
                <v-card-text>
                    <p>Время создания запроса:<br/> {{this.start_datetime}}</p>
                    <p>Время завершения операции:<br/> {{this.end_datetime}}</p>
                    <p>Кадров с детекциями: {{this.frames.length }}</p>
                    <v-btn class="mt-5" color="primary" width="100%" variant="flat" :href="this.host + '/result/' + this.id">Результат</v-btn>
                </v-card-text>
            </v-col>
        </v-row>
        <v-row width="100%">
            <p class="text-h6 text-md-h5 text-lg-h4 ma-7 ">Инциденты:</p>
        </v-row>
        
        <v-row
          align="start"
          no-gutters
        >
        
        <v-col
            v-for="n in this.frames"
            :key="n"
            class="mr-10 mb-10"
          >
          <div class="ma-4">
            <a :href="this.host + '/frames/' + this.id + '/' + n" target="_blank">
            <v-img
                class="bg-grey-lighten-4"
                width="500"
                :aspect-ratio="1"
                :src="this.host + '/frames/' + this.id + '/' + n"
            >
            </v-img>
          </a>
            </div>
          </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  import axios from "axios"

    export default {
        data () {
        return {
            dialog: false,
            name: "Test",
            frames: [],
            start_datetime: "000",
            end_datetime: "000",
            host: "http://195.239.123.50:9090",
            preview: "src/assets/test.png"
        }
        },
        props: ["id"],
        methods: {
            getFrames() {
                axios.get(this.host + '/frames/' + this.id)
                .then((resp) => {
                console.log(resp)
                this.frames = resp.data
            }).catch(function (er) {
                console.log(er);
            });
            },
            getOrder() {
                axios.get(this.host + '/order/' + this.id)
                .then((resp) => {
                console.log(resp)
                this.name = resp.data.title
                this.start_datetime = resp.data.created_at
                this.end_datetime = resp.data.finished_at
            }).catch(function (er) {
                console.log(er);
            });
            }
        },
        mounted() {
            this.getFrames()
            this.getOrder()
        }
    }
  </script>
  