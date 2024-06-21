import axios from 'axios';

export async function calculateAlignment(sequence1: string, sequence2: string) {
    try {
        const response = await axios.post('/align', {
            sequence1,
            sequence2
        });
        const { alignment, eValue,  gaps,score } = response.data; // 提取返回值
        // console.log(alignment)
        return {
            alignment,
            eValue,
            score,
            gaps
        };
    } catch (error) {
        console.error('Error calculating alignment:', error);
        return {
            alignment: 'Error',
            eValue: 'Error',
            score: 'Error',
            gaps: 'Error'
        };
    }
}
