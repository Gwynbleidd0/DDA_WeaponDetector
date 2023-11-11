<template>
    <v-container class=" mb-6">
        <v-row justify="end" class="mb-5 mt-5">
            <!-- <v-col
                cols="2"
            > -->
            <CreateOrder></CreateOrder>

        </v-row>
        <v-row
        align="start"
        no-gutters
      >
        <v-col
            v-for="n in this.orders"
            :key="n"
            class=""
            cols="4"
          >
          <ReportCard :name="n.title" :id="n.id" class="mr-10 mb-10"/>
          </v-col>
        </v-row>
      <!-- <v-responsive class="align-center text-center fill-height">
        
      </v-responsive> -->
    </v-container>
  </template>
  
  <script>
  import CreateOrder from "@/components/CreateOrder.vue";
  import ReportCard from "@/components/ReportCard.vue";
  import axios from "axios"


export default {
    name: "ReportsView",
    components: {
        CreateOrder,
        ReportCard
    },
    data () {
      return {
        orders: [],
      }
    },
    methods: {
        getAllReports() {
            axios.get('http://195.239.123.50:9090/orders/'
            ).then((resp) => {
                console.log(resp)
                this.diffOrders(resp.data)
            }).catch(function (er) {
                console.log(er);
            });
            },
        diffOrders(data) {
          let diff = data.filter(x => !this.orders.map(y => y.id).includes(x.id))
          console.log(data.map(y => y.id))
          console.log(this.orders.map(y => y.id))
          console.log(diff)
          for(let i of diff) {
            console.log(i)
            this.orders.push(i)
          }
        }
        },
    mounted() {
        this.getAllReports()
        setInterval(() => {
            this.getAllReports()
        }, 5000);
    },
    }
  </script>
  