<template>
    <v-container>
        <v-card 
        variant="outlined"
        rounded="lg"
        elevation="1" 
        style="min-width: 400px; border-color: rgba(0, 0, 0, 0.2)">
            <v-card-title>
                Список отчетов
            </v-card-title>
            <v-divider />
            <v-card-text>
                <v-text-field label="Поиск" v-model="finder" v-on:keyup="find" />

                <v-list v-if="filteredReports.length > 0" style="text-align: left">
                    <v-list-item v-for="report in filteredReports">
                        <router-link v-bind:to="{name: 'reportInfo', params: {reportId: report.id}}"> {{ report.name }} </router-link>
                    </v-list-item>
                </v-list>

                <v-list v-else-if="noMatchFound"> 
                    <v-list-item> Совпадений не найдено </v-list-item>
                </v-list>
            
                <v-list v-else>
                    <v-list-item v-for="report in reports" style="text-align: left">
                        <router-link v-bind:to="{name: 'reportInfo', params: {reportId: report.id}}"> {{ report.name }} </router-link>
                    </v-list-item>
                </v-list>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
import reports from "../assets/reports.json"
export default {
    data() {
        return {
            finder: "",
            filteredReports: [],
            noMatchFound: false
        }
    },
    methods: {
        find() {
            //this.reports.find(r => r === this.finder)
            if (!/[a-zA-Z0-9А-Яа-яЁё]/.test(this.finder)) {
                this.filteredReports = [];
                this.noMatchFound = false;
                return;
            }
            const search = this.finder.toLowerCase();
            this.filteredReports = this.reports.filter(r => 
                r.name.toLowerCase().includes(search)
            );
            this.noMatchFound = false;

            if (this.finder && this.filteredReports.length === 0) {
                this.noMatchFound = true;
            }
        }
    },
    computed: {
        reports() {
            return reports.reports;
        }
    }
}
</script>