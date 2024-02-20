/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks"
const { Component, onWillStart, useRef, onMounted, useState } = owl
import { getColor } from "@web/views/graph/colors"

moment.locale('fa'); // Set the locale to Persian

export class OwlSalesDashboard extends Component {
    // top 5 Properties
    async getTopProperties(){
        // applying domain
        let domain = [['current_status', '=', 'use']]
        if (this.state.period > 0){
            domain.push(['date_availability','>', this.state.current_date])
        }
        const data = await this.orm.readGroup("real.estate", domain, ['name', 'expected_price'], ['name'], { limit: 2, orderby: "date_availability desc" })

        this.state.topProperties = {
            data: {
                labels: data.map(d => d.name[1]),
                  datasets: [
                  {
                    label: 'Expected Price',
                    data: data.map(d => d.expected_price),
                    hoverOffset: 4,
                    // for different colors
                    backgroundColor : data.map((_, index) => getColor(index)),
                  },{
                    label: 'Count',
                    data: data.map(d => d.selling_price),
                    hoverOffset: 4,
                     // for different colors
                    backgroundColor : data.map((_, index) => getColor(index)),
                     }]
                 }
                }
            }

    // top 5 Tenants people
    async getTopTenants(){
         // applying domain
        let domain = [['is_paid', '=', 'true']]

        const data = await this.orm.readGroup("tenant.payment", domain, ['tenant_id', 'amount'], ['tenant_id'], { limit: 5, orderby: "months desc" })

        this.state.topTenants = {
            data: {
                labels: data.map(d => d.tenant_id[1]),
                  datasets: [
                  {
                    label: 'Total Amount',
                    data: data.map(d => d.amount),
                    hoverOffset: 4,
                    // for different colors
                    backgroundColor : data.map((_, index) => getColor(index)),
                  }]
            }
         }

        }


async getMonthlySales() {
    let paidDomain = [['is_paid', '=', true]];
    let unpaidDomainBase = [['is_paid', '=', false]];

    if (this.state.period > 0) {
        paidDomain.push(['months', '>', this.state.current_date]);
        unpaidDomainBase.push(['months', '>', this.state.current_date]);
    }

    const paidData = await this.orm.readGroup("tenant.payment", paidDomain, ['tenant_id', 'amount'], ['tenant_id'], { orderby: "months", lazy: false });
    const unpaidData = await this.orm.readGroup("tenant.payment", unpaidDomainBase, ['tenant_id', 'amount'], ['tenant_id'], { orderby: "months", lazy: false });

    const labels = paidData.map(d => d.tenant_id[1]);
    const paidAmounts = paidData.map(d => d.amount);

    const unpaidDatasets = unpaidData.map(unpaid => ({
        label: `Unpaid Amount - ${unpaid.tenant_id[1]}`,
        data: [null, unpaid.amount], // Add null for alignment with paid amounts
        hoverOffset: 4,
        backgroundColor: "#00c698",
    }));

    this.state.monthlySales = {
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Paid Amount',
                    data: paidAmounts,
                    hoverOffset: 4,
                    backgroundColor: "#b84c7d",
                },
                ...unpaidDatasets,
            ],
        },
    };
}


    // partner orders
//  async getPartnerOffers() {
//    let currentMonth = new Date().getMonth() + 1; // Get the current month (1-12)
//
//    let offerDomain = [['status', '=', 'accepted'], ['create_date', '>=', moment().startOf('month').format('YYYY-MM-DD')]];
//
//    const partners = await this.orm.readGroup("estate.property.offer", offerDomain, ['partner_id'], ['partner_id'], { orderby: "partner_id", lazy: false });
//
//    let labels = [];
//    let offerAmounts = [];
//
//    const datasets = await Promise.all(partners.map(async partner => {
//        const partnerOfferDomain = [...offerDomain, ['partner_id', '=', partner.partner_id[0]]];
//        const partnerOfferData = await this.orm.readGroup("estate.property.offer", partnerOfferDomain, ['price'], ['partner_id'], { orderby: "create_date", lazy: false });
//
//        const partnerLabels = [partner.partner_id[1]];
//        const partnerOfferAmounts = partnerOfferData.map(d => d.price);
//
//        labels = [...labels, ...partnerLabels];
//        offerAmounts = [...offerAmounts, ...partnerOfferAmounts];
//
//        return {
//            label: `${partner.partner_id[1]}'s Offers`,
//            data: partnerOfferAmounts,
//            hoverOffset: 4,
//            backgroundColor: "red",
//        };
//    }));
//
//    this.state.PartnerOffers = {
//        data: {
//            labels: labels,
//            datasets: datasets,
//        },
//    };


async getAllOffersByProperty() {
    let sixMonthsAgo = moment().subtract(6, 'months').startOf('month').format('YYYY-MM-DD');
    let offerDomain = [['create_date', '>=', sixMonthsAgo]];

    const properties = await this.orm.readGroup("estate.property.offer", offerDomain, ['property_id', 'status'], ['property_id', 'status'], { orderby: "property_id", lazy: false });

    let labels = [];
    let allOfferAmounts = [];
    let acceptedOfferAmounts = [];

    for (const property of properties) {
        const propertyLabels = [property.property_id[1]];
        const propertyAllOfferCount = property.__count; // Total number of offers for the property
        const propertyAcceptedOfferCount = property.status === 'accepted' ? property.__count : 0; // Number of accepted offers

        labels.push(propertyLabels[0]);  // Push the first label (property name) only once
        allOfferAmounts.push(propertyAllOfferCount - propertyAcceptedOfferCount);  // Subtract accepted offers from total offers
        acceptedOfferAmounts.push(propertyAcceptedOfferCount);
    }

    this.state.AllPropertyOffers = {
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'All Offers',
                    data: allOfferAmounts,
                    hoverOffset: 4,
                    backgroundColor: "blue",
                },
                {
                    label: 'Accepted Offers',
                    data: acceptedOfferAmounts,
                    hoverOffset: 4,
                    backgroundColor: "green",
                },
            ],
        },
    };
}


    setup(){
        this.state = useState({
            properties: {
                value:10,
                percentage:6,
            },
            period:90,
        })
        this.orm = useService("orm")
        this.actionService = useService("action")

        onWillStart(async ()=>{
            this.getDates()
            await this.getProperties()
            await this.getOffers()
            await this.getPayments()
            await this.getAgents()

            await this.getTopProperties()
            await this.getTopTenants()
            await this.getMonthlySales()

            await this.getAllOffersByProperty()

        })
    }

    async onChangePeriod(){
        this.getDates()
        await this.getProperties()
        await this.getOffers()
        await this.getPayments()
        await this.getAgents()

    }

    getDates(){
        this.state.current_date = moment().subtract(this.state.period, 'days').format('YYYY-MM-DD')
        this.state.previous_date = moment().subtract(this.state.period * 2, 'days').format('YYYY-MM-DD')
    }

    async getProperties(){
        let domain = [['current_status', 'in', ['use', 'not_use']]]
        if (this.state.period > 0){
            domain.push(['date_availability','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("real.estate", domain)
        this.state.properties.value = data

        // previous period
        let prev_domain = [['current_status', 'in', ['use', 'not_use']]]
        if (this.state.period > 0){
            prev_domain.push(['date_availability','>', this.state.previous_date], ['date_availability','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("real.estate", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        this.state.properties.percentage = percentage.toFixed(2)
    }
    // show offer in dashboard
    async getOffers(){
        let domain = [['status', 'in', ['accepted', 'refused', null]]]
        if (this.state.period > 0){
            domain.push(['deadline','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("estate.property.offer", domain)
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['status', 'in', ['accepted', 'refused',null]]]
        if (this.state.period > 0){
            prev_domain.push(['deadline','>', this.state.previous_date], ['deadline','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("estate.property.offer", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100
        //this.state.quotations.percentage = percentage.toFixed(2)

        this.state.offers = {
            value: data,
            percentage: percentage.toFixed(2),
        }

    }

    //show Tenants paid payment in dashboard
    async getPayments(){
        let domain = [['is_paid', '=', 'true']]
        if (this.state.period > 0){
            domain.push(['payment_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("tenant.payment", domain)
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['is_paid', '=', 'true']]
        if (this.state.period > 0){
            prev_domain.push(['payment_date','>', this.state.previous_date], ['payment_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("tenant.payment", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100


        this.state.payments = {
            value: data,
            percentage: percentage.toFixed(2),

        }

        //this.env.services.company
    }

    // get All agents
    async getAgents(){
        let domain = [['agent_name', '!=', null]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }
        const data = await this.orm.searchCount("agent.view", domain)
        //this.state.quotations.value = data

        // previous period
        let prev_domain = [['agent_name', '!=', null]]
        if (this.state.period > 0){
            prev_domain.push(['create_date','>', this.state.previous_date], ['create_date','<=', this.state.current_date])
        }
        const prev_data = await this.orm.searchCount("agent.view", prev_domain)
        const percentage = ((data - prev_data)/prev_data) * 100

        this.state.agents = {
            value: data,
            percentage: percentage.toFixed(2),

        }

    }

    // get all properties
    async viewProperties(){
        let domain = [['current_status', 'in', ['use', 'not_use']]]
        if (this.state.period > 0){
            domain.push(['date_availability','>', this.state.current_date])
        }

        let list_view = await this.orm.searchRead("ir.model.data", [['name', '=', 'view_advertise_tree']], ['res_id'])

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Properties",
            res_model: "real.estate",
            domain,
            views: [
                [list_view.length > 0 ? list_view[0].res_id : false, "list"],
                [false, "form"],
            ]
        })
    }

    viewOffers(){
        let domain = [['status', 'in', ['accepted', 'refused',null]]]
        if (this.state.period > 0){
            domain.push(['deadline','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Offers",
            res_model: "estate.property.offer",
            domain,
            context: {group_by: ['property_id']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }
    // return into tenant.payment view
    viewPayments(){
        let domain = [['is_paid', 'in', [true, false]]]
        if (this.state.period > 0){
            domain.push(['payment_date','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Tenant Paid Payments",
            res_model: "tenant.payment",
            domain,
            context: {group_by: ['months']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }

    // return into agent.view
    viewAgents(){
        let domain = [['agent_name', '!=', null]]
        if (this.state.period > 0){
            domain.push(['create_date','>', this.state.current_date])
        }

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Agents",
            res_model: "agent.view",
            domain,
            context: {group_by: ['agent_property_id']},
            views: [
                [false, "list"],
                [false, "form"],
            ]
        })
    }
}

OwlSalesDashboard.template = "owl.OwlSalesDashboard"
OwlSalesDashboard.components = { KpiCard, ChartRenderer }

registry.category("actions").add("owl.egp_property_dashboard", OwlSalesDashboard)