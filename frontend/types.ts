interface serverData {
    page: pages,
    data: prematch | matchBar | postmatch | leaderboard | null
}

type pages = 'welcome' | 'prematch' | 'matchbar' | 'postmatch' | 'leaderboard';

type team = {
    name: string,
    id: string
}

type leaderboardTeam = {
    name: string,
    id: string,
    score: string
}

interface prematch {
    title: string,
    redTeams: team[],
    blueTeams: team[]
}

interface matchBar {
    title: string,
    redTeamIDs: string[],
    blueTeamIDs: string[],
    redScore: string,
    blueScore: string,
    remainingTime: string,
    scoreCheckInProgress: boolean,
    matchbarVisible: boolean,
    attackerAlliance: number, // 0 for Red, 1 for Blue, 2 for Endgame
    preStartCountdown?: number | null,
    streamUrl?: string,
    streamEnabled?: boolean,
    refereeState?: {
        red: {
            minorFaul: number,
            majorFaul: number,
            fuelCount: number,
            climbCount: number,
            climbSelections: ("L1" | "L2" | "L3" | null)[]
        },
        blue: {
            minorFaul: number,
            majorFaul: number,
            fuelCount: number,
            climbCount: number,
            climbSelections: ("L1" | "L2" | "L3" | null)[]
        }
    }
}

interface postmatch {
    title: string,
    redTeams: team[],
    blueTeams: team[],
    pointTypes: string[],
    redPoints: string[],
    bluePoints: string[],
    redScore: string,
    blueScore: string,
    winner: number
}

//winner: 0 = tie, 1 = Red, 2 = Blue

interface leaderboard {
    "teams": leaderboardTeam[]
}


export type {pages, serverData, prematch, matchBar, postmatch, leaderboard, team, leaderboardTeam}
