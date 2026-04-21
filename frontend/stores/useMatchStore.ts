import {defineStore} from 'pinia'
import type { pages, prematch, matchBar, postmatch, leaderboard } from '@/types';

export const useMatchStore = defineStore('match', () => {
    let postMatch: Ref<postmatch> = ref({
        title: '',
        redTeams: [],
        blueTeams: [],
        pointTypes: [],
        redPoints: [],
        bluePoints: [],
        redScore: "",
        blueScore: "",
        winner: 0
    })
    let matchBar: Ref<matchBar> = ref({
        title: '',
        page: '',
        redTeamIDs: [],
        blueTeamIDs: [],
        redScore: "",
        blueScore: "",
        remainingTime: "",
        scoreCheckInProgress: false,
        matchbarVisible: true,
        attackerAlliance: 0,
        preStartCountdown: null,
        streamUrl: '',
        streamEnabled: true,
        refereeState: {
            red: {
                minorFaul: 0,
                majorFaul: 0,
                fuelCount: 0,
                climbCount: 0,
                climbSelections: [null, null, null]
            },
            blue: {
                minorFaul: 0,
                majorFaul: 0,
                fuelCount: 0,
                climbCount: 0,
                climbSelections: [null, null, null]
            }
        }
    })

    let preMatch: Ref<prematch> = ref({
        title: '',
        redTeams: [],
        blueTeams: []
    })

    let leaderboard: Ref<leaderboard> = ref({
        teams: []
    })
    let currentPage: Ref<pages> = ref('welcome')

    // Setter for postMatch
    const setPostMatch = (data: postmatch) => {
        postMatch.value = data
    }

    const setMatchBar = (data: matchBar) => {
        matchBar.value = data
    }
    const setPreMatch = (data: prematch) => {
        preMatch.value = data
    }
    const setLeaderboard = (data: leaderboard) => {
        leaderboard.value = data
    }
    const setCurrentPage = (page: pages) => {
        currentPage.value = page
    }
    return {
        setPostMatch,
        setMatchBar,
        setPreMatch,
        setLeaderboard,
        setCurrentPage,
        postMatch,
        matchBar,
        preMatch,
        leaderboard,
        currentPage
    }
}, {persist: true})
