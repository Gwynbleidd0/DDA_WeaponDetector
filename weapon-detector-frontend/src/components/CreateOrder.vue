<template>
<v-btn append-icon="mdi-plus" color="primary" variant="flat">
        Добавить видео 
        <v-dialog
            v-model="dialog"
            activator="parent"
            width="500"
        >
            <v-card title="Dialog">
                <form>

                <v-card-text>
                        <v-text-field
                        :counter="32"
                        required
                        ref="title"
                        v-on:change="handleTitleEdit()"
                        name="title"
                        label="Name"
                        ></v-text-field>
                        <v-file-input accept="video/*" required v-on:change="handleFileUpload()" ref="file" label="Видео" name="file"></v-file-input>

                   
                </v-card-text>

                <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text="Добавить"
                    :disabled = "this.isProcessed"
                    @click="this.sendNewItem()"
                ></v-btn>
                <v-btn
                    text="Отмена"
                    color="red"
                    @click="dialog = false"
                ></v-btn>
                </v-card-actions>
            </form>
            </v-card>
        </v-dialog>
    </v-btn>
</template>
<script >
import axios from "axios"

export default {
    name: 'CreateOrder',
    data () {
        return {
        dialog: false,
        title: null,
        file: null,
        isProcessed: false
        }
    },
    methods: {
        handleFileUpload() {
            this.file = this.$refs.file.files[0];
        },
        handleTitleEdit() {
            this.title = this.$refs.title.value
        },
        sendNewItem() {
            this.isProcessed = true;
            let formData = new FormData();
            formData.append('file', this.file);
            formData.append('title', this.title);
            console.log(formData)
            axios.post('http://195.239.123.50:9090/order',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }
            ).then((resp) => {
                console.log(this);
                console.log(resp)
                this.isProcessed = false;
                this.dialog = false
                this.$emit('add-event')
            }).catch(function (er) {
                console.log(er);
                this.isProcessed = false;
            });
        }
    }
    }
</script>